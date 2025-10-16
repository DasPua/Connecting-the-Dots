import React from "react";
import { BookOpen } from "lucide-react";

const OutlineSidebar = ({ outline, title }) => {
  return (
    <div className="w-80 border rounded-2xl shadow-lg bg-white p-5 overflow-y-auto h-[90vh]">
      {outline ? (
        <div>
          <h2 className="text-xl font-bold mb-4 text-gray-700 flex items-center gap-2">
            <BookOpen className="text-blue-600" size={22} />
            <span>{title || "Untitled Document"}</span>
          </h2>
          <ul className="space-y-3">
            {outline.map((item, idx) => (
              <li
                key={idx}
                className="border-b pb-2 hover:bg-blue-50 rounded-lg px-2 transition"
              >
                <span className="text-blue-600 font-medium">
                  {item.level}
                </span>{" "}
                - {item.text}{" "}
                <span className="text-gray-500 text-sm">
                  (Page {item.page})
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-gray-500 text-center mt-20">
          No outline extracted yet.
        </p>
      )}
    </div>
  );
};

export default OutlineSidebar;
