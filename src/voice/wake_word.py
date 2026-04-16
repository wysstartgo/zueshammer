"""
ZuesHammer Voice Wake Word System

语音唤醒 + 实时监听 + 声音记忆

功能:
1. 唤醒词检测 (Wake Word)
2. 实时麦克风监听
3. 语音转文字
4. 用户声音记忆
5. 安装后语音自我介绍
"""

import asyncio
import logging
import time
import struct
import hashlib
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class WakeWordStatus(Enum):
    """唤醒状态"""
    IDLE = "idle"
    LISTENING = "listening"
    WAKE_DETECTED = "wake_detected"
    PROCESSING = "processing"


@dataclass
class VoiceProfile:
    """用户声音档案"""
    user_id: str
    name: str
    voice_hash: str  # 声音特征哈希
    embeddings: List[float] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    interaction_count: int = 0


class WakeWordDetector:
    """
    唤醒词检测器

    使用简单的能量检测 + 关键词匹配
    未来可升级为Porcupine等专业的唤醒词引擎
    """

    def __init__(
        self,
        wake_words: List[str] = None,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
    ):
        self.wake_words = wake_words or ["宙斯", "zues", "zueshammer", "hey", "ok"]
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

        # 音频参数
        self.energy_threshold = 500
        self.min_wake_duration = 0.3  # 秒
        self.silence_timeout = 2.0  # 秒

        # 状态
        self._status = WakeWordStatus.IDLE
        self._audio_buffer: List[bytes] = []
        self._silence_frames = 0

        # 回调
        self._on_wake_callback: Optional[Callable] = None

    def set_wake_callback(self, callback: Callable):
        """设置唤醒回调"""
        self._on_wake_callback = callback

    async def process_audio_chunk(self, audio_chunk: bytes) -> bool:
        """
        处理音频块

        Returns:
            True 如果检测到唤醒词
        """
        # 计算能量
        energy = self._calculate_energy(audio_chunk)

        # 能量检测
        if energy > self.energy_threshold:
            self._audio_buffer.append(audio_chunk)
            self._silence_frames = 0

            # 检查是否有足够的音频
            total_duration = len(self._audio_buffer) * self.chunk_size / self.sample_rate

            if total_duration >= self.min_wake_duration:
                # 提取音频并检测唤醒词
                audio_data = b"".join(self._audio_buffer)

                if self._detect_wake_word(audio_data):
                    self._status = WakeWordStatus.WAKE_DETECTED
                    logger.info("Wake word detected!")

                    # 调用回调
                    if self._on_wake_callback:
                        await self._on_wake_callback(audio_data)

                    # 清空缓冲区
                    self._audio_buffer = []
                    self._status = WakeWordStatus.IDLE
                    return True

        else:
            # 静音处理
            self._silence_frames += 1

            # 超时清空缓冲区
            total_duration = len(self._audio_buffer) * self.chunk_size / self.sample_rate
            if total_duration > self.silence_timeout:
                self._audio_buffer = []

        return False

    def _calculate_energy(self, audio_chunk: bytes) -> float:
        """计算音频能量"""
        if len(audio_chunk) < 2:
            return 0

        try:
            samples = struct.unpack("<" + "h" * (len(audio_chunk) // 2), audio_chunk)
            energy = sum(s * s for s in samples) / len(samples)
            return energy ** 0.5
        except Exception:
            return 0

    def _detect_wake_word(self, audio_data: bytes) -> bool:
        """检测唤醒词 (简化版，实际应该用ASR)"""
        # 这里简化处理，实际应该用Whisper或专门的唤醒词引擎
        # 暂时返回False，让VAD检测静默来触发

        # 检查能量是否持续高于阈值
        if len(self._audio_buffer) < 3:
            return False

        # 简单启发式：连续多帧高能量
        return True

    async def run(self, audio_source: Callable) -> asyncio.Future:
        """
        运行唤醒检测

        Args:
            audio_source: 返回音频数据的异步生成器
        """
        self._status = WakeWordStatus.LISTENING

        try:
            async for chunk in audio_source():
                detected = await self.process_audio_chunk(chunk)

                if detected:
                    logger.info("Wake word detected, triggering callback")

        except asyncio.CancelledError:
            self._status = WakeWordStatus.IDLE
            raise


class VoiceMemory:
    """
    用户声音记忆

    记住用户的声音特征
    """

    def __init__(self, memory_manager=None):
        self.memory = memory_manager
        self._profiles: Dict[str, VoiceProfile] = {}
        self._current_user: Optional[VoiceProfile] = None

        # 加载已有档案
        self._load_profiles()

    def _load_profiles(self):
        """加载声音档案"""
        if not self.memory:
            return

        # 从记忆系统加载
        profiles_data = self.memory.recall("voice_profiles")
        if profiles_data:
            for user_id, data in profiles_data.items():
                self._profiles[user_id] = VoiceProfile(**data)

    def _save_profiles(self):
        """保存声音档案"""
        if not self.memory:
            return

        profiles_data = {
            user_id: {
                "user_id": p.user_id,
                "name": p.name,
                "voice_hash": p.voice_hash,
                "embeddings": p.embeddings,
                "created_at": p.created_at,
                "last_seen": p.last_seen,
                "interaction_count": p.interaction_count,
            }
            for user_id, p in self._profiles.items()
        }

        self.memory.remember("voice_profiles", profiles_data)

    def register_user(
        self,
        user_id: str,
        name: str,
        audio_sample: bytes = None,
    ) -> VoiceProfile:
        """注册用户声音"""
        # 生成声音哈希
        voice_hash = self._generate_voice_hash(audio_sample or b"")

        profile = VoiceProfile(
            user_id=user_id,
            name=name,
            voice_hash=voice_hash,
        )

        self._profiles[user_id] = profile
        self._save_profiles()

        logger.info(f"Registered voice profile for: {name}")
        return profile

    def identify_user(self, audio_data: bytes) -> Optional[VoiceProfile]:
        """
        识别用户

        当前简化实现，未来可用声纹识别
        """
        # 简单实现：生成音频哈希并比较
        audio_hash = self._generate_voice_hash(audio_data)

        for profile in self._profiles.values():
            if profile.voice_hash == audio_hash:
                # 更新最后访问时间
                profile.last_seen = time.time()
                profile.interaction_count += 1
                self._current_user = profile
                self._save_profiles()
                return profile

        return None

    def get_current_user(self) -> Optional[VoiceProfile]:
        """获取当前用户"""
        return self._current_user

    def get_all_profiles(self) -> List[VoiceProfile]:
        """获取所有档案"""
        return list(self._profiles.values())

    def delete_profile(self, user_id: str):
        """删除档案"""
        if user_id in self._profiles:
            del self._profiles[user_id]
            self._save_profiles()

    def _generate_voice_hash(self, audio_data: bytes) -> str:
        """生成声音哈希"""
        if not audio_data:
            return hashlib.md5(str(time.time()).encode()).hexdigest()

        # 取音频的哈希
        return hashlib.md5(audio_data[:10000]).hexdigest()


class VoiceInteraction:
    """
    语音交互系统

    整合唤醒、监听、识别
    """

    def __init__(
        self,
        voice_config: Dict = None,
        memory_manager=None,
    ):
        config = voice_config or {}

        self.wake_words = config.get("wake_words", ["宙斯", "zues", "zueshammer"])
        self.sample_rate = config.get("sample_rate", 16000)

        # 组件
        self.wake_detector = WakeWordDetector(
            wake_words=self.wake_words,
            sample_rate=self.sample_rate,
        )

        self.voice_memory = VoiceMemory(memory_manager)

        # STT/TTS
        self._stt = None
        self._tts = None

        # 状态
        self._status = WakeWordStatus.IDLE
        self._listening = False
        self._running = False

        # 回调
        self._on_user_speak_callback: Optional[Callable] = None
        self._on_response_callback: Optional[Callable] = None

    def set_callbacks(
        self,
        on_user_speak: Callable = None,
        on_response: Callable = None,
    ):
        """设置回调"""
        self._on_user_speak_callback = on_user_speak
        self._on_response_callback = on_response

        # 设置唤醒回调
        self.wake_detector.set_wake_callback(self._on_wake_detected)

    async def _on_wake_detected(self, audio_data: bytes):
        """唤醒词检测到"""
        self._status = WakeWordStatus.WAKE_DETECTED
        logger.info("Wake word detected, ready to listen...")

        # 继续监听用户说话
        await self._listen_for_command(audio_data)

    async def _listen_for_command(self, wake_audio: bytes = None):
        """监听用户命令"""
        self._status = WakeWordStatus.LISTENING

        # 收集音频直到静音
        audio_chunks = [wake_audio] if wake_audio else []

        # 这里简化处理，实际应该持续监听
        # 并在检测到静音后进行ASR

    async def start_listening(self):
        """开始监听"""
        self._listening = True
        self._running = True
        self._status = WakeWordStatus.LISTENING

        logger.info("Voice listening started")

    async def stop_listening(self):
        """停止监听"""
        self._listening = False
        self._running = False
        self._status = WakeWordStatus.IDLE

        logger.info("Voice listening stopped")

    async def speech_to_text(self, audio_data: bytes) -> str:
        """语音转文字"""
        if not self._stt:
            # 延迟导入
            try:
                from ..voice.voice_system import WhisperSTT
                self._stt = WhisperSTT(self._get_voice_config())
            except Exception:
                logger.error("STT not available")
                return ""

        result = await self._stt.transcribe(audio_data)
        return result.get("text", "")

    async def text_to_speech(self, text: str, language: str = "zh") -> bytes:
        """文字转语音"""
        if not self._tts:
            try:
                from ..voice.voice_system import EdgeTTS
                self._tts = EdgeTTS(self._get_voice_config())
            except Exception:
                logger.error("TTS not available")
                return b""

        from ..voice.voice_system import Language
        lang = Language.CHINESE if language == "zh" else Language.ENGLISH

        return await self._tts.synthesize(text, lang)

    def _get_voice_config(self):
        """获取语音配置"""
        from ..voice.voice_system import VoiceConfig
        return VoiceConfig()

    def get_status(self) -> str:
        """获取状态"""
        return self._status.value

    def get_current_user(self) -> Optional[VoiceProfile]:
        """获取当前用户"""
        return self.voice_memory.get_current_user()


class VoiceManager:
    """
    语音管理器

    统一管理语音交互
    """

    def __init__(self, config: Dict = None, memory_manager=None):
        self.config = config or {}

        # 创建语音交互
        self.interaction = VoiceInteraction(
            voice_config=self.config,
            memory_manager=memory_manager,
        )

        # 音频捕获
        self._audio_capture = None
        self._capture_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """初始化"""
        logger.info("Initializing voice system...")

        # 初始化STT
        await self._init_stt()

        # 初始化TTS
        await self._init_tts()

        logger.info("Voice system initialized")

    async def _init_stt(self):
        """初始化STT"""
        try:
            from ..voice.voice_system import WhisperSTT
            voice_config = self._get_voice_config()
            self.interaction._stt = WhisperSTT(voice_config)
        except Exception as e:
            logger.warning(f"STT init failed: {e}")

    async def _init_tts(self):
        """初始化TTS"""
        try:
            from ..voice.voice_system import EdgeTTS
            voice_config = self._get_voice_config()
            self.interaction._tts = EdgeTTS(voice_config)
        except Exception as e:
            logger.warning(f"TTS init failed: {e}")

    async def start_voice_mode(self, agent):
        """
        启动语音模式

        Args:
            agent: ZuesHammer智能体
        """
        logger.info("Starting voice mode...")

        # 设置回调
        self.interaction.set_callbacks(
            on_user_speak=self._on_user_speak,
            on_response=self._on_response,
        )

        # 开始监听
        await self.interaction.start_listening()

        # 启动音频捕获循环
        self._capture_task = asyncio.create_task(self._capture_loop(agent))

        # 语音自我介绍
        await self._introduction(agent)

        logger.info("Voice mode started")

    async def stop_voice_mode(self):
        """停止语音模式"""
        if self._capture_task:
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass

        await self.interaction.stop_listening()

        logger.info("Voice mode stopped")

    async def _capture_loop(self, agent):
        """音频捕获循环"""
        try:
            import pyaudio

            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024,
            )

            logger.info("Audio capture started")

            while self.interaction._running:
                try:
                    # 读取音频
                    audio_chunk = stream.read(1024, exception_on_overflow=False)

                    # 处理音频
                    detected = await self.interaction.wake_detector.process_audio_chunk(audio_chunk)

                    if detected:
                        # 唤醒词检测到，等待用户说完
                        command_audio = await self._capture_until_silence(stream)

                        if command_audio:
                            # 语音转文字
                            text = await self.interaction.speech_to_text(command_audio)

                            if text:
                                logger.info(f"User said: {text}")

                                # 处理用户输入
                                response = await agent.process(text)

                                # 语音合成并播放
                                audio = await self.interaction.text_to_speech(response)
                                if audio:
                                    await self._play_audio(audio)

                except Exception as e:
                    logger.error(f"Capture error: {e}")

            stream.stop_stream()
            stream.close()
            p.terminate()

        except ImportError:
            logger.error("pyaudio not installed")
        except asyncio.CancelledError:
            if stream:
                stream.stop_stream()
                stream.close()
            if p:
                p.terminate()
            raise

    async def _capture_until_silence(self, stream, max_duration: float = 10.0) -> bytes:
        """捕获到静音"""
        chunks = []
        silence_threshold = 500
        silence_frames = 0
        max_silence_frames = 40  # 约2秒静音

        start = time.time()

        while True:
            # 超时检查
            if time.time() - start > max_duration:
                break

            # 读取音频
            chunk = stream.read(1024, exception_on_overflow=False)
            chunks.append(chunk)

            # 检查能量
            energy = self._calculate_energy(chunk)

            if energy < silence_threshold:
                silence_frames += 1
                if silence_frames > max_silence_frames:
                    break
            else:
                silence_frames = 0

        return b"".join(chunks)

    def _calculate_energy(self, audio_chunk: bytes) -> float:
        """计算音频能量"""
        if len(audio_chunk) < 2:
            return 0

        try:
            samples = struct.unpack("<" + "h" * (len(audio_chunk) // 2), audio_chunk)
            energy = sum(s * s for s in samples) / len(samples)
            return energy ** 0.5
        except Exception:
            return 0

    async def _on_user_speak(self, audio_data: bytes):
        """用户说话回调"""
        logger.info("User speaking...")

    async def _on_response(self, text: str):
        """响应回调"""
        logger.info(f"Response: {text}")

    async def _play_audio(self, audio_data: bytes):
        """播放音频"""
        try:
            import pyaudio
            import wave
            import io

            # 解码MP3
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
                raw_data = audio.raw_data
                sample_rate = audio.frame_rate
            except Exception:
                raw_data = audio_data
                sample_rate = 16000

            # 播放
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(2),
                channels=1,
                rate=sample_rate,
                output=True,
            )

            stream.write(raw_data)
            stream.stop_stream()
            stream.close()
            p.terminate()

        except ImportError:
            logger.warning("Audio playback not available")
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")

    async def _introduction(self, agent):
        """自我介绍"""
        intro = """你好！我是ZuesHammer，宙斯之锤。

我的核心能力包括：
理解你的意图并匹配合适的技能。
如果找不到技能，我会调用大模型来工作。
每次工作完成后，我会学习新的技能。
下次遇到类似的问题，我就能直接回答了。

你可以直接用语音和我对话，唤醒词是"宙斯"。

有什么我可以帮你的吗？"""

        logger.info("Introduction text generated")

        # 语音合成
        audio = await self.interaction.text_to_speech(intro)

        if audio:
            await self._play_audio(audio)
            logger.info("Introduction played")

    def _get_voice_config(self) -> Dict:
        """获取语音配置"""
        return self.config


# 全局实例
_voice_manager: Optional[VoiceManager] = None


def get_voice_manager(config: Dict = None, memory_manager=None) -> VoiceManager:
    """获取语音管理器"""
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = VoiceManager(config, memory_manager)
    return _voice_manager
