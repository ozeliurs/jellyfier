import React, { useEffect, useState } from "react";
import { getFiles, deleteFiles, deleteAllFiles } from "../api/files";
import FileTable from "../components/FileTable";

const FileList: React.FC = () => {
  const [files, setFiles] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAllFiles = async () => {
      let allFiles: any[] = [];
      let skip = 0;
      const limit = 10;
      let fetchedFiles: any[];

      do {
        fetchedFiles = await getFiles(skip, limit);
        allFiles = [...allFiles, ...fetchedFiles];
        skip += limit;
      } while (fetchedFiles.length === limit);

      setFiles(allFiles);
      setLoading(false);
    };

    fetchAllFiles();
  }, []);

  const handleDelete = async (ids: number[]) => {
    await deleteFiles(ids);
    setFiles(files.filter((file) => !ids.includes(file.id)));
  };

  const handleDeleteAll = async () => {
    await deleteAllFiles();
    setFiles([]);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

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
