import os
from typing import List, Union, Iterator, Optional, Callable
from typing_extensions import Self
import enum

class FileOrFolder(enum.Enum):
    """
        Stores state of a DirectoryObject if it is a folder or file
    """
    FILE = "file"
    FOLDER = "folder"


class DirectoryObject:
    """
        Hierarically stores the directory structure\n
        Important methods:
            name() -> get name of object
            is_file() -> True if object is file
            is_folder() -> True if object is folder
            get_number_of_files(level=-1) -> get total number of files upto the given level, -1 for infinite depth
            get_number_of_folders(level=-1) -> similar to get_number_of_files(level)
            get_depth() -> get depth of the directory tree
            get_files() -> get a list of DirectoryObject immediately inside the folder
            get_folders() -> similar to get_files()
    """
    _name: str
    _is_file_or_folder: FileOrFolder
    _folders: List[Self]
    _files: List[Self]

    def __init__(self, 
        name: str, 
        is_file_or_folder: FileOrFolder=FileOrFolder.FILE,
        list_of_folders: Optional[List[Self]]=None, 
        list_of_files: Optional[List[Self]]=None
    ) -> None:
        self._name = os.path.basename(name)
        self._is_file_or_folder = is_file_or_folder
        self._folders = list_of_folders or []
        self._files = list_of_files or []
        self._folders.sort()
        self._files.sort()

    def name(self) -> str:
        return self._name
    

    def is_folder(self) -> bool:
        """returns True if the calling object is a folder otherwise False"""
        return self._is_file_or_folder == FileOrFolder.FOLDER
    

    def is_file(self) -> bool:
        """returns True if the calling object is a file otherwise False"""
        return self._is_file_or_folder == FileOrFolder.FILE
    

    def add_folder(self, folder: Union[Self, List[Self]]) -> None:
        if isinstance(folder, DirectoryObject):
            if not folder.is_folder():
                return
            
            self._folders.append(folder)
        
        else: # folder is a list
            self._folders += [f for f in folder if f.is_folder()]
    

    def add_file(self, files: Union[Self, List[Self]]) -> None:
        if isinstance(files, DirectoryObject):
            if not files.is_file():
                return
            
            self._files.append(files)
        
        else: # files is a list
            self._files += [f for f in files if f.is_file()]

    
    def get_number_of_files(self, level: int=-1, file_extension: str | list[str] | None=None) -> int:
        """
            Get number of files inside the folder
            @level: int 
                = 0 for only current folder
                = any negative number for all files inside nested folders
                = any positive number of level of nesting to count up to
            
            returns 1 if the object upon which this function is being called at is 
            a file
        """

        # If file_extension is there and it is a single file extension,
        # convert it to a list
        if file_extension:
            if isinstance(file_extension, str):
                file_extension = [file_extension]
        else:
            file_extension = []
        
        if self.is_file():
            if file_extension:
                if any([self._name.lower().endswith(ext.lower()) for ext in file_extension]):
                    return 1
                else:
                    return 0
            return 1
        
        if level == 0:
            return len([f for f in self._files if any([f.name().lower().endswith(ext.lower()) for ext in file_extension])])
        
        return sum([f.get_number_of_files(level=level-1, file_extension=file_extension) for f in self._folders + self._files])
    

    def get_number_of_folders(self, level: int=-1) -> int:
        """
            Get number of folders inside the folder, 0 if the calling object is a file
            @level: int 
                = 0 for only current folder
                = any negative number for all files inside nested folders
                = any positive number of level of nesting to count up to
        """
        if level == 0:
            return len(self._folders)
        
        return len(self._folders) + sum([f.get_number_of_folders(level=level-1) for f in self._folders])
    

    def get_depth(self) -> int:
        """Returns upto how much depth is the tree created"""
        return 1 + max([f.get_depth() for f in self._folders], default=-1)

    def get_folders(self) -> Iterator[Self]:
        for f in self._folders:
            yield f
    
    def get_files(self) -> Iterator[Self]:
        for f in self._files:
            yield f

    def __str__(self) -> str:
        def get_string(folder: DirectoryObject, indent_level: int=0, dir_prefix: str="(dir)", file_prefix: str="(file)") -> str:
            string = ""
            for subfolder in folder.get_folders():
                string += "\t" * indent_level + f"{dir_prefix}{subfolder.name()}\n"
                string += get_string(subfolder, indent_level=indent_level+1)
            
            for file in folder.get_files():
                string += "\t" * indent_level + f"{file_prefix}{file.name()}\n"
            
            return string
        return f"{os.path.basename(self._name)}\n" + get_string(self)
    
    def __repr__(self) -> str:
        return f"""DirectoryObject({"(file)" if self.is_file() else "(dir)"}{self._name})"""
    
    def __lt__(self, other: Self) -> bool:
        return os.path.basename(self._name) < os.path.basename(other._name)
    

def create_directory_tree(folder: Optional[str]=None, level: int=-1, allow_folder_function: Callable[[str], bool]=lambda _: True) -> DirectoryObject:
    if folder is None:
        folder = os.curdir
    
    if os.path.exists(folder) and os.path.isdir(folder):
        pass
    else:
        raise ValueError("Argument should be a valid directory")
    
    folders: list[str] = []
    files: list[str] = []
    for _, folders, files in os.walk(folder):
        folders = [os.path.join(_, f) for f in folders if allow_folder_function(f)]
        folders.sort()
        files.sort()
        break


    if level == 0:
        return DirectoryObject(
            folder, 
            FileOrFolder.FOLDER, 
            [DirectoryObject(f, FileOrFolder.FOLDER) for f in folders],
            [DirectoryObject(f, FileOrFolder.FILE) for f in files]
            )

    folder_list: List[DirectoryObject] = []
    files_list: List[DirectoryObject] = [DirectoryObject(f, FileOrFolder.FILE) for f in files]

    for f in folders:
        folder_list.append(create_directory_tree(f, level=level-1))
    
    return DirectoryObject(folder, FileOrFolder.FOLDER, folder_list, files_list)


if __name__ == '__main__':
    print(create_directory_tree(".", level=1))#, allow_folder_function=_allow_folder_func))