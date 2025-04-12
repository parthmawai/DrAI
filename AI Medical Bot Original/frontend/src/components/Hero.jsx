import React from "react";

const Hero = ({ title, imageUrl }) => {
  return (
    <>
      <div className="hero container">
        <div className="banner">
          <h1>Welcome to Dr AI | Your Trusted AI-Powered Healthcare Assistant</h1>
          <p>
          At Dr. AI, we believe in harnessing the power of AI to make healthcare more accessible, efficient, and patient-centric. Our cutting-edge voice-based medical assistant ensures that anyone, regardless of language barriers or location, can receive timely medical advice. With intelligent diagnosis and automated appointment booking, we are revolutionizing telemedicine for a healthier tomorrow.
          </p>
        </div>
        <div className="banner">
          <img src={imageUrl} alt="hero" className="animated-image" />
          <span>
            <img src="/Vector.png" alt="vector" />
          </span>
        </div>
      </div>
    </>
  );
};

export default Hero;
