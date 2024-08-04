from typing import Optional

class InvImage:
    url: str
    width: int
    height: int

class InvThumbnail:
    quality: str
    url: str
    width: int
    height: int

class InvVideo:
    type: str
    title: str
    videoId: str
    author: str
    authorId: str
    authorUrl: str
    authorVerified: bool
    videoThumbnails: list[InvThumbnail]
    description: str
    descriptionHtml: str
    viewCount: int
    viewCountText: str
    lengthSeconds: int
    published: int
    publishedText: str
    premiereTimestamp: Optional[int]
    liveNow: bool
    premium: bool
    isUpcoming: bool

class InvChannel:
    type: str
    author: str
    authorId: str
    authorUrl: str
    authorVerified: bool
    authorThumbnails: list[InvThumbnail]
    autoGenerated: False
    subCount: int
    videoCount: int
    description: str
    descriptionHtml: str

class InvPlaylistVideo:
    title: str
    videoId: str
    lengthSeconds: int
    videoThumbnails: list[InvThumbnail]

class InvPlaylist:
    type: str
    title: str
    playlistId: str
    playlistThumbnail: str
    author: str
    authorId: str
    authorUrl: str
    authorVerified: bool
    videoCount: int
    videos: list[InvPlaylistVideo]

class InvStoryboard:
    url: str
    templateUrl: str
    width: int
    height: int
    count: int
    interval: int
    storyboardWidth: int
    storyboardHeight: int
    storyboardCount: int

class InvAuthorThumbnail:
    url: str
    width: int
    height: int

class InvAdaptiveFormat:
    index: str
    bitrate: str
    init: str
    url: str
    itag: str
    type: str
    clen: str
    lmt: str
    projectionType: int
    fps: int
    container: str
    encoding: str
    audioQuality: Optional[str]
    audioSampleRate: Optional[int]
    audioChannels: Optional[int]
    qualityLabel: Optional[str]
    resolution: Optional[str]
    colorInfo: dict[str, str]

class InvFormatStream:
    url: str
    itag: str
    type: str
    quality: str
    bitrate: str
    fps: int
    container: str
    encoding: str
    qualityLabel: str
    resolution: str
    size: str

class InvCaption:
    label: str
    languageCode: str
    url: str

class InvRecommendedVideo:
    videoId: str
    title: str
    videoThumbnails: list[InvThumbnail]
    author: str
    authorId: str
    authorUrl: str
    authorVerified: bool
    lengthSeconds: int
    viewCount: int
    viewCountText: str

class InvFullVideo:
    type: str
    title: str
    videoId: str
    videoThumbnails: list[InvThumbnail]
    storyboards: list[InvStoryboard]
    description: str
    descriptionHtml: str
    published: int
    publishedText: str
    keywords: list[str]
    viewCount: int
    likeCount: int
    dislikeCount: int
    paid: bool
    premium: bool
    isFamilyFriendly: bool
    allowedRegions: list[str]
    genre: str
    genreUrl: str
    author: str
    authorId: str
    authorUrl: str
    authorVerified: bool
    authorThumbnails: list[InvAuthorThumbnail]
    subCountText: str
    lengthSeconds: int
    allowRatings: bool
    rating: float
    isListed: bool
    liveNow: bool
    isPostLiveDvr: bool
    isUpcoming: bool
    dashUrl: str
    premiereTimestamp: Optional[int]
    hlsUrl: Optional[str]
    adaptiveFormats: list[InvAdaptiveFormat]
    formatStreams: list[InvFormatStream]
    captions: list[InvCaption]
    recommendedVideos: list[InvRecommendedVideo]

    def get_best_audio(self):
        # for format in self.adaptiveFormats:
        #     if not format.audioQuality:
        pass