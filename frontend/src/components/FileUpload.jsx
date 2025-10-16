import React from "react";
import { Upload, Loader2 } from "lucide-react";

const FileUpload = ({ file, setFile, handleUpload, loading }) => {
  return (
    <div className="flex items-center justify-center">
      <div className="bg-white shadow-lg rounded-2xl p-6 flex items-center gap-4 border border-gray-200 hover:shadow-xl transition-shadow duration-200">
        <label className="flex items-center gap-2 cursor-pointer bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium px-4 py-2 rounded-lg border border-blue-200 transition-all">
          <Upload size={20} />
          <span>{file ? file.name : "Choose PDF"}</span>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="hidden"
          />
        </label>

        <button
          onClick={handleUpload}
          disabled={loading}
          className={`flex items-center justify-center gap-2 px-6 py-2 rounded-lg font-semibold text-white transition-all duration-200 ${
            loading
              ? "bg-blue-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={18} /> Processing...
            </>
          ) : (
            "Extract Outline"
          )}
        </button>
      </div>
    </div>
  );
};

export default FileUpload;
