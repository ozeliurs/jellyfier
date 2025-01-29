import React, { useEffect, useState } from "react";
import { getFiles, deleteFiles, deleteAllFiles } from "../api/files";
import FileTable from "../components/FileTable";

const FileList: React.FC = () => {
  const [files, setFiles] = useState<any[]>([]);

  useEffect(() => {
    const fetchFiles = async () => {
      const data = await getFiles();
      setFiles(data);
    };

    fetchFiles();
  }, []);

  const handleDelete = async (ids: number[]) => {
    await deleteFiles(ids);
    setFiles(files.filter((file) => !ids.includes(file.id)));
  };

  const handleDeleteAll = async () => {
    await deleteAllFiles();
    setFiles([]);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Files</h1>
      <FileTable
        files={files}
        onDelete={handleDelete}
        onDeleteAll={handleDeleteAll}
      />
    </div>
  );
};

export default FileList;
