from typing import Optional


class User:
    '''
    User info object
    '''
    def __init__(
            self,
            username: str,
            md5: str,
            role: int,
            displayedName: Optional[str] = None,
            displayed_name: Optional[str] = None,
    ) -> None:
        self.username = username
        self.md5 = md5
        self.role = role
        self.displayed_name = displayed_name or displayedName
