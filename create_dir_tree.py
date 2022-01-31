import os
from typing import List, Dict, Union, Iterator
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
    _folders: List["DirectoryObject"]
    _files: List["DirectoryObject"]

    def __init__(self, 
        name: str, 
        is_file_or_folder=FileOrFolder.FILE,
        list_of_folders: List["DirectoryObject"]=None, 
        list_of_files: List["DirectoryObject"]=None
    ) -> None:
        self._name = name
        self._is_file_or_folder = is_file_or_folder
        self._folders = list_of_folders or []
        self._files = list_of_files or []
    

    def name(self) -> str:
        return self._name
    

    def is_folder(self) -> bool:
        """returns True if the calling object is a folder otherwise False"""
        return self._is_file_or_folder == FileOrFolder.FOLDER
    

    def is_file(self) -> bool:
        """returns True if the calling object is a file otherwise False"""
        return self._is_file_or_folder == FileOrFolder.FILE
    

    def add_folder(self, folder: Union["DirectoryObject", List["DirectoryObject"]]) -> None:
        if isinstance(folder, DirectoryObject):
            if not folder.is_folder():
                return
            
            self._folders.append(folder)
        
        else: # folder is a list
            self._folders += [f for f in folder if f.is_folder()]
    

    def add_file(self, files: Union["DirectoryObject", List["DirectoryObject"]]) -> None:
        if isinstance(files, DirectoryObject):
            if not files.is_file():
                return
            
            self._files.append(files)
        
        else: # files is a list
            self._files += [f for f in files if f.is_file()]

    
    def get_number_of_files(self, level: int=-1) -> int:
        """
            Get number of files inside the folder
            @level: int 
                = 0 for only current folder
                = any negative number for all files inside nested folders
                = any positive number of level of nesting to count up to
            
            returns 1 if the object upon which this function is being called at is 
            a file
        """
        if self.is_file():
            return 1
        
        if level == 0:
            return len(self._files)
        
        return len(self._files) + sum([f.get_number_of_files(level=level-1) for f in self._folders])
    

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

    def get_folders(self) -> Iterator["DirectoryObject"]:
        for f in self._folders:
            yield f
    
    def get_files(self) -> Iterator["DirectoryObject"]:
        for f in self._files:
            yield f

    def __str__(self) -> str:
        def get_string(folder: DirectoryObject, indent_level: int=0, dir_prefix="", file_prefix="") -> str:
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
    

def create_directory_tree(folder: str=None, level: int=-1, filter_func=lambda x: True) -> DirectoryObject:
    if folder is None:
        folder = os.curdir
    
    if os.path.exists(folder) and os.path.isdir(folder):
        pass
    else:
        raise ValueError("Argument should be a valid directory")
    
    for _, folders, files in os.walk(folder):
        folders = [os.path.join(_, f) for f in folders if filter_func(f)]
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

def _filter_func(x: str) -> bool:
    return not x.startswith(".")


if __name__ == '__main__':
    print(create_directory_tree(".", level=1))#, filter_func=_filter_func))