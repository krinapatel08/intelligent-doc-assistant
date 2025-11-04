import { useState } from "react";
import { toast } from "sonner";

export function FileUpload({ onUpload }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return toast.error("Please select a file first!");
    setLoading(true);
    try {
      await onUpload(file);
      toast.success("File uploaded successfully!");
      setFile(null);
    } catch (err) {
      toast.error("Upload failed!");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-xl text-center border border-gray-700">
      <h3 className="text-lg font-semibold mb-2">Upload a Document</h3>
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleChange}
        className="block w-full text-sm text-gray-300 file:mr-3 file:py-2 file:px-4 file:rounded-md 
                   file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white 
                   hover:file:bg-blue-700 mb-3"
      />
      <button
        onClick={handleUpload}
        disabled={loading}
        className={`w-full py-2 rounded-md font-medium transition ${
          loading
            ? "bg-gray-600 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {loading ? "Uploading..." : "Upload"}
      </button>
    </div>
  );
}
