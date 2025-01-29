import React, { useState } from "react";

interface File {
  id: number;
  filepath: string;
  filename: string;
  file_extension: string;
  file_size: number;
  video_codec?: string;
  video_resolution?: string;
}

interface FileTableProps {
  files: File[];
  onDelete: (ids: number[]) => void;
  onDeleteAll: () => void;
}

const FileTable: React.FC<FileTableProps> = ({
  files,
  onDelete,
  onDeleteAll,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<number[]>([]);

  const handleSelectFile = (id: number) => {
    setSelectedFiles((prev) =>
      prev.includes(id)
        ? prev.filter((fileId) => fileId !== id)
        : [...prev, id],
    );
  };

  const handleSelectAll = () => {
    setSelectedFiles(
      files.length === selectedFiles.length ? [] : files.map((file) => file.id),
    );
  };

  return (
    <div>
      <button
        onClick={() => onDelete(selectedFiles)}
        className="btn btn-danger"
      >
        Delete Selected
      </button>
      <button onClick={onDeleteAll} className="btn btn-danger">
        Delete All
      </button>
      <table className="table-auto w-full mt-4">
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                checked={files.length === selectedFiles.length}
                onChange={handleSelectAll}
              />
            </th>
            <th>Filename</th>
            <th>File Extension</th>
            <th>File Size</th>
            <th>Video Codec</th>
            <th>Video Resolution</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.id}>
              <td>
                <input
                  type="checkbox"
                  checked={selectedFiles.includes(file.id)}
                  onChange={() => handleSelectFile(file.id)}
                />
              </td>
              <td>{file.filename}</td>
              <td>{file.file_extension}</td>
              <td>{file.file_size}</td>
              <td>{file.video_codec}</td>
              <td>{file.video_resolution}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FileTable;
