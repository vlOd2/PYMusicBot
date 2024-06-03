class Version:
    _major : int
    _minor : int
    _revision : int
    _subtype : str

    def __init__(self, major : int, minor : int, revision : int, subtype : str = None) -> None:
        self._major = major
        self._minor = minor
        self._revision = revision
        self._subtype = subtype

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor
    
    @property
    def revision(self) -> int:
        return self._revision

    @property
    def subtype(self) -> str:
        return self._subtype

    @staticmethod
    def from_str(s : str):
        ver_subtype = s.strip().split("-", 1)
        ver_raw = ver_subtype[0].strip().split(".", 2)
        major = int(ver_raw[0])
        minor = int(ver_raw[1])
        revision = int(ver_raw[2])
        return Version(major, minor, revision, ver_subtype[1].strip() if len(ver_subtype) > 1 else None)
    
    def __str__(self) -> str:
        return (f"{self._major}.{self._minor}.{self._revision}" + 
            (f"-{self._subtype}" if self._subtype != None else ""))
    
    def __eq__(self, other : object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        ver : Version = other
        return (self.major == ver.major and 
                self.minor == ver.minor and 
                self.revision == ver.revision and
                ((self.subtype == None and ver.subtype == None) or self.subtype == ver.subtype))
    
    def __lt__(self, other : object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        ver : Version = other
        return (self.major < ver.major or 
                self.minor < ver.minor or 
                self.revision < ver.revision)
    
    def __le__(self, other : object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        ver : Version = other
        return (self.major <= ver.major or 
                self.minor <= ver.minor or 
                self.revision <= ver.revision)
    
    def __gt__(self, other : object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        ver : Version = other
        return (self.major > ver.major or 
                self.minor > ver.minor or 
                self.revision > ver.revision)
    
    def __ge__(self, other : object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        ver : Version = other
        return (self.major >= ver.major or 
                self.minor >= ver.minor or 
                self.revision >= ver.revision)