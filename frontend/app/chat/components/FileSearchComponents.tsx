"use client";

import React, { useState, useCallback } from "react";
import { useCopilotReadable } from "@copilotkit/react-core";

export interface FileUploadStatus {
  filename: string;
  status: "uploading" | "success" | "error";
  message?: string;
  file_id?: string;
}

export interface SearchResult {
  query: string;
  results: string;
  sources: string[];
}

export function FileUploadCard() {
  const [uploadedFiles, setUploadedFiles] = useState<FileUploadStatus[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  // Make uploaded files readable by the agent
  useCopilotReadable({
    description: "List of files uploaded by the user",
    value: uploadedFiles,
  });

  const handleFileUpload = useCallback(async (files: FileList) => {
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
      // Add file to uploading state
      setUploadedFiles((prev) => [
        ...prev,
        {
          filename: file.name,
          status: "uploading",
          message: "Uploading...",
        },
      ]);

      try {
        const formData = new FormData();
        formData.append("file", file);

        // Upload to backend
        const response = await fetch("/api/upload-file", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.filename === file.name && f.status === "uploading"
                ? {
                    filename: file.name,
                    status: "success",
                    message: "Uploaded successfully",
                    file_id: result.file_id,
                  }
                : f
            )
          );
        } else {
          throw new Error("Upload failed");
        }
      } catch (error) {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.filename === file.name && f.status === "uploading"
              ? {
                  filename: file.name,
                  status: "error",
                  message: "Upload failed",
                }
              : f
          )
        );
      }
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files) {
        handleFileUpload(e.dataTransfer.files);
      }
    },
    [handleFileUpload]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          isDragging
            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
            : "border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500"
        }`}
      >
        <div className="flex flex-col items-center gap-4">
          <div className="text-6xl">📁</div>
          <div>
            <h3 className="text-lg font-semibold mb-2">Upload Files</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Drag and drop files here, or click to browse
            </p>
            <label className="inline-block">
              <input
                type="file"
                multiple
                onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                className="hidden"
                accept=".txt,.pdf,.doc,.docx,.md"
              />
              <span className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg cursor-pointer transition-colors inline-block">
                Choose Files
              </span>
            </label>
          </div>
          <p className="text-xs text-gray-500">
            Supported: .txt, .pdf, .doc, .docx, .md
          </p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <span>📚</span>
            <span>Uploaded Files ({uploadedFiles.length})</span>
          </h4>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <FileStatusItem key={`${file.filename}-${index}`} file={file} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function FileStatusItem({ file }: { file: FileUploadStatus }) {
  const statusConfig = {
    uploading: {
      icon: "⏳",
      color: "text-yellow-600 dark:text-yellow-400",
      bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
    },
    success: {
      icon: "✅",
      color: "text-green-600 dark:text-green-400",
      bgColor: "bg-green-50 dark:bg-green-900/20",
    },
    error: {
      icon: "❌",
      color: "text-red-600 dark:text-red-400",
      bgColor: "bg-red-50 dark:bg-red-900/20",
    },
  };

  const config = statusConfig[file.status];

  return (
    <div
      className={`flex items-center justify-between p-3 rounded-lg ${config.bgColor}`}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <span className="text-2xl">{config.icon}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{file.filename}</p>
          {file.message && (
            <p className={`text-sm ${config.color}`}>{file.message}</p>
          )}
        </div>
      </div>
      {file.status === "uploading" && (
        <div className="animate-spin">⚙️</div>
      )}
    </div>
  );
}

export function SearchResultCard({ result }: { result: SearchResult }) {
  return (
    <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-6 text-white shadow-xl mt-4">
      <div className="flex items-start gap-3">
        <span className="text-3xl">🔍</span>
        <div className="flex-1">
          <h3 className="text-xl font-bold mb-2">Search Results</h3>
          <div className="bg-white/20 rounded-lg p-4 mb-4">
            <p className="text-sm font-semibold mb-1">Query:</p>
            <p className="italic">{result.query}</p>
          </div>
          <div className="bg-white/20 rounded-lg p-4">
            <p className="text-sm font-semibold mb-2">Results:</p>
            <p className="whitespace-pre-wrap">{result.results}</p>
          </div>
          {result.sources && result.sources.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold mb-2">Sources:</p>
              <div className="flex flex-wrap gap-2">
                {result.sources.map((source, index) => (
                  <span
                    key={index}
                    className="bg-white/30 px-3 py-1 rounded-full text-sm"
                  >
                    📄 {source}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
