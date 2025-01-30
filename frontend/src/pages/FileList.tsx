import React, { useEffect, useState } from "react";
import { getFiles, deleteFiles, deleteAllFiles } from "../api/files";
import FileTable from "../components/FileTable";
import { PieChart } from "@mui/x-charts/PieChart";
import { Grid, Typography } from "@mui/material";

const FileList: React.FC = () => {
  const [files, setFiles] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAllFiles = async () => {
      let allFiles: any[] = [];
      let skip = 0;
      const limit = 500;
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

  const getDistributionData = (key: string) => {
    const distribution = files.reduce((acc, file) => {
      const value = file[key];
      if (value) {
        acc[value] = (acc[value] || 0) + 1;
      }
      return acc;
    }, {});

    return Object.keys(distribution).map((key) => ({
      id: key,
      label: key,
      value: distribution[key],
    }));
  };

  const getNestedDistributionData = (key: string, nestedKey: string) => {
    const distribution = files.reduce((acc, file) => {
      const nestedArray = file[key];
      if (nestedArray) {
        nestedArray.forEach((item: any) => {
          const value = item[nestedKey];
          if (value) {
            acc[value] = (acc[value] || 0) + 1;
          }
        });
      }
      return acc;
    }, {});

    return Object.keys(distribution).map((key) => ({
      id: key,
      label: key,
      value: distribution[key],
    }));
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold mb-4">Files</h1>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6} lg={3}>
          <Typography variant="h6" gutterBottom>
            File Types
          </Typography>
          <PieChart
            series={[
              {
                data: getDistributionData("file_extension"),
              },
            ]}
            width={200}
            height={200}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Typography variant="h6" gutterBottom>
            Video Codecs
          </Typography>
          <PieChart
            series={[
              {
                data: getDistributionData("video_codec"),
              },
            ]}
            width={200}
            height={200}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Typography variant="h6" gutterBottom>
            Audio Channels
          </Typography>
          <PieChart
            series={[
              {
                data: getNestedDistributionData("audio_channels", "channel"),
              },
            ]}
            width={200}
            height={200}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Typography variant="h6" gutterBottom>
            Subtitle Channels
          </Typography>
          <PieChart
            series={[
              {
                data: getNestedDistributionData(
                  "subtitle_channels",
                  "subtitle",
                ),
              },
            ]}
            width={200}
            height={200}
          />
        </Grid>
      </Grid>
      <FileTable
        files={files}
        onDelete={handleDelete}
        onDeleteAll={handleDeleteAll}
      />
    </div>
  );
};

export default FileList;
