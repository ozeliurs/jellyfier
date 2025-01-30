import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getFile, deleteFile } from "../api/files";

const FileView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [file, setFile] = useState<any>(null);

  useEffect(() => {
    const fetchFile = async () => {
      if (id) {
        const data = await getFile(parseInt(id));
        setFile(data);
      }
    };

    fetchFile();
  }, [id]);

  const handleDelete = async () => {
    if (id) {
      await deleteFile(parseInt(id));
      navigate("/");
    }
  };

  if (!file) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">File Details</h1>
      <div className="mb-4">
        <h2 className="text-xl font-semibold">Audio Channels</h2>
        <table className="table table-zebra w-full mt-2">
          <thead>
            <tr>
              <th>Name</th>
              <th>Channel</th>
              <th>Codec</th>
            </tr>
          </thead>
          <tbody>
            {file.audio_channels.map((channel: any) => (
              <tr key={channel.id}>
                <td>{channel.name}</td>
                <td>{channel.channel}</td>
                <td>{channel.codec}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mb-4">
        <h2 className="text-xl font-semibold">Subtitle Channels</h2>
        <table className="table table-zebra w-full mt-2">
          <thead>
            <tr>
              <th>Name</th>
              <th>Subtitle</th>
              <th>Codec</th>
            </tr>
          </thead>
          <tbody>
            {file.subtitle_channels.map((channel: any) => (
              <tr key={channel.id}>
                <td>{channel.name}</td>
                <td>{channel.subtitle}</td>
                <td>{channel.codec}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button onClick={handleDelete} className="btn btn-danger">
        Delete File
      </button>
    </div>
  );
};

export default FileView;
