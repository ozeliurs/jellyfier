import axios from "axios";

const API_URL = "http://localhost:8000/files";

export const getFiles = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const getFile = async (id: number) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const deleteFile = async (id: number) => {
  await axios.delete(`${API_URL}/${id}`);
};

export const deleteFiles = async (ids: number[]) => {
  await Promise.all(ids.map((id) => deleteFile(id)));
};

export const deleteAllFiles = async () => {
  const files = await getFiles();
  await deleteFiles(files.map((file: any) => file.id));
};
