import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./index.css";
import FileList from "./pages/FileList";
import FileView from "./pages/FileView";

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<FileList />} />
        <Route path="/files/:id" element={<FileView />} />
      </Routes>
    </Router>
  </React.StrictMode>,
  document.getElementById("root"),
);
