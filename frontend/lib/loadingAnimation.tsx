import React from "react";
import "./loadingAnimation.css";

interface LoadingAnimationProps {
    text?: string;
}

export default function LoadingAnimation({ text }: LoadingAnimationProps) {
  return (
    <div className="loading">
      <div className="loading_spinner">
        <i className="fa-solid fa-fire-burner" />
      </div>
      <p className="loading_text">{text || "Loading..."}</p>
    </div>
  );
}