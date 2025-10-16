import React, { useState, useRef } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import axios from "axios";
import UploadPage from "./pages/UploadPage";
import ViewerPage from "./pages/ViewerPage";

function App() {
  const [file, setFile] = useState(null);
  const [outline, setOutline] = useState(null);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const adobeDCViewRef = useRef(null);

  const handleUpload = async (navigate) => {
    if (!file) return alert("Please select a PDF file first!");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/extract_outline`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setTitle(res.data.title);
      setOutline(res.data.outline);
      navigate("/viewer"); // go to next page
    } catch (err) {
      console.error(err);
      alert("Failed to process the PDF");
    } finally {
      setLoading(false);
    }
  };

  const displayPDF = (file) => {
  if (!window.AdobeDC) {
    alert("Adobe PDF Embed SDK not loaded");
    return;
  }

  if (!adobeDCViewRef.current) {
    adobeDCViewRef.current = new window.AdobeDC.View({
      clientId: import.meta.env.VITE_ADOBE_CLIENT_ID, // use env variable
      divId: "adobe-dc-view",
    });
  }

  const reader = new FileReader();
  reader.onloadend = (e) => {
    const arrayBuffer = e.target.result;
    adobeDCViewRef.current.previewFile(
      {
        content: { promise: Promise.resolve(arrayBuffer) },
        metaData: { fileName: file.name },
      },
      {
        embedMode: "FULL_WINDOW",
        showDownloadPDF: true,
        showPrintPDF: true,
      }
    );
  };
  reader.readAsArrayBuffer(file);
};


  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <UploadPage
              file={file}
              setFile={setFile}
              handleUpload={handleUpload}
              loading={loading}
            />
          }
        />
        <Route
          path="/viewer"
          element={
            <ViewerPage
              file={file}
              outline={outline}
              title={title}
              displayPDF={displayPDF}
            />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
