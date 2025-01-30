import React, { useState } from "react";
import { Link } from "react-router-dom";
import { formatSize } from "../utils/formatSize";

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
      <div className="overflow-x-auto mt-4">
        <table className="table table-zebra w-full">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  className="checkbox"
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
                    className="checkbox"
                    checked={selectedFiles.includes(file.id)}
                    onChange={() => handleSelectFile(file.id)}
                  />
                </td>
                <td>
                  <Link
                    to={`/files/${file.id}`}
                    className="text-blue-500 hover:underline"
                  >
                    {file.filename}
                  </Link>
                </td>
                <td>{file.file_extension}</td>
                <td>{formatSize(file.file_size)}</td>
                <td>{file.video_codec}</td>
                <td>{file.video_resolution}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th></th>
              <th>Filename</th>
              <th>File Extension</th>
              <th>File Size</th>
              <th>Video Codec</th>
              <th>Video Resolution</th>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default FileTable;
