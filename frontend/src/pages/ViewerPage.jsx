import React, { useEffect } from "react";
import OutlineSidebar from "../components/OutlineSidebar";
import PDFViewer from "../components/PDFViewer";

const ViewerPage = ({ file, outline, title, displayPDF }) => {
  useEffect(() => {
    if (file) {
      displayPDF(file);
    }
  }, [file]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white p-6 flex flex-col gap-6">
      {/* Header */}
      <header className="w-full bg-white shadow-md rounded-2xl p-4 text-center">
        <h1 className="text-3xl font-bold text-blue-700">{title || "Document Viewer"}</h1>
      </header>

      {/* Main content */}
      <div className="flex flex-col lg:flex-row gap-6 mt-4">
        {/* PDF Viewer */}
        <div className="flex-1 bg-white rounded-2xl shadow-lg p-2 h-[75vh] lg:h-[90vh] overflow-hidden">
          <PDFViewer />
        </div>

        {/* Outline Sidebar */}
        <div className="w-full lg:w-80 bg-white rounded-2xl shadow-lg p-5 h-[50vh] lg:h-[90vh] overflow-y-auto">
          <OutlineSidebar outline={outline} title={title} />
        </div>
      </div>
    </div>
  );
};

export default ViewerPage;
