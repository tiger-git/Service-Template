from abc import ABC
from typing import ClassVar, Dict, Type, Union, Optional
from pathlib import Path
from dataclasses import dataclass


import fitz


@dataclass
class FileSource:
    """统一文件源描述"""
    data: Union[bytes, str, Path]  # bytes数据 / 本地路径 / OSS URL
    filename: Optional[str] = None  # 用于从bytes推断后缀
    source_type: str = "auto"  # "local" | "oss" | "bytes"
    
    @classmethod
    def from_bytes(cls, data: bytes, filename: str) -> 'FileSource':
        return cls(data=data, filename=filename, source_type="bytes")
    
    @classmethod
    def from_path(cls, path: Union[str, Path]) -> 'FileSource':
        return cls(data=path, filename=Path(path).name, source_type="local")
    
    @classmethod
    def from_oss(cls, url: str, filename: Optional[str] = None) -> 'FileSource':
        return cls(data=url, filename=filename or url.split('/')[-1], source_type="oss")
    
    @property
    def suffix(self) -> str:
        """获取文件后缀（不含点）"""
        if self.filename:
            return Path(self.filename).suffix.lower().lstrip('.')
        return ""


class FileParse(ABC):
    _registry: ClassVar[Dict[str, Type['FileParse']]] = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        file_types = getattr(cls, 'file_types', None)
        if not file_types:
            raise ValueError(f"{cls.__name__} 必须定义 'file_types' 类变量")
        for file_type in file_types:
            cls._registry[file_type.lower()] = cls

    def parse(self, source: FileSource, **kwargs) -> str:
        """解析入口，子类实现此方法"""
        raise NotImplementedError

    @classmethod
    def get_parser(cls, source: Union[str, Path, bytes, FileSource]) -> 'FileParse':
        """根据文件源自动获取解析器实例"""
        # 统一转为 FileSource
        if isinstance(source, FileSource):
            file_source = source
        elif isinstance(source, bytes):
            raise ValueError("bytes类型必须包装为 FileSource 并提供 filename")
        else:  # str or Path
            file_source = FileSource.from_path(source)
        
        suffix = file_source.suffix
        if not suffix:
            raise ValueError("无法确定文件类型，请提供 filename")
        
        parser_cls = cls._registry.get(suffix)
        if not parser_cls:
            raise ValueError(f"不支持的文件类型: .{suffix}")
        
        return parser_cls()

    @classmethod
    def parse_file(cls, source: Union[str, Path, FileSource], **kwargs) -> str:
        """一键解析"""
        parser = cls.get_parser(source)
        return parser.parse(source, **kwargs)


# ──────────────────────────────────────────────
# 具体解析器实现
# ──────────────────────────────────────────────

class ParsePdf(FileParse):
    file_types = ['pdf']
    
    def parse(self, source: FileSource, **kwargs) -> str:
        if source.source_type == "bytes":
            # 处理 bytes 数据
            return self._parse_from_bytes(source.data, **kwargs)
        elif source.source_type == "oss":
            # 从 OSS 下载后解析
            return self._parse_from_oss(source.data, **kwargs)
        else:
            # 本地文件
            return self._parse_from_local(source.data, **kwargs)
    
    def _parse_from_local(self, file_path: Union[str, Path], **kwargs) -> str:
        # 本地 PDF 解析逻辑
        doc = fitz.open(file_path)
        full_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            full_text.append(text)
        return "\n\n".join(full_text)
    
    def _parse_from_oss(self, url: str, **kwargs) -> str:
        # OSS PDF 解析逻辑（如下载后解析）
        return f"[PDF] 解析 OSS 文件: {url}"
    
    def _parse_from_bytes(self, data: bytes, **kwargs) -> str:
        # bytes PDF 解析逻辑
        return f"[PDF] 解析 bytes 数据，大小: {len(data)} 字节"



if __name__ == "__main__":
    file = FileSource.from_path("static/docs/亿达科创差旅费管理制度.pdf")
    FileParse.parse_file(file)