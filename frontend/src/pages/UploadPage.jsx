import React from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud } from "lucide-react";

const UploadPage = ({ file, setFile, handleUpload, loading }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-blue-50 to-blue-100 p-6">
      <h1 className="text-5xl font-extrabold text-blue-700 mb-10 drop-shadow-sm text-center">
        Connecting The Dots
      </h1>

      {/* Upload Box */}
      <div className="w-full max-w-md bg-white rounded-3xl shadow-lg border-2 border-dashed border-blue-300 p-10 flex flex-col items-center gap-6 hover:border-blue-500 transition-all duration-300">
        <UploadCloud className="text-blue-500 w-16 h-16" />
        <h2 className="text-xl font-semibold text-gray-700 text-center">
          {file ? `Selected File: ${file.name}` : "Drag & Drop your PDF here"}
        </h2>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="hidden"
          id="pdf-upload"
        />
        <label
          htmlFor="pdf-upload"
          className="cursor-pointer bg-blue-600 text-white font-semibold px-6 py-3 rounded-xl hover:bg-blue-700 transition-all"
        >
          {file ? "Change File" : "Select PDF"}
        </label>

        <button
          onClick={() => handleUpload(navigate)}
          disabled={loading || !file}
          className={`w-full mt-3 py-3 rounded-xl font-semibold text-white transition-all duration-200 ${
            loading || !file
              ? "bg-blue-300 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {loading ? "Processing..." : "Extract Outline"}
        </button>
      </div>

      <p className="text-gray-500 mt-6 text-center text-sm">
        Upload a PDF file to extract its outline automatically.
      </p>
    </div>
  );
};

export default UploadPage;
