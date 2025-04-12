import React from "react";

const Biography = ({imageUrl}) => {
  return (
    <>
      <div className="container biography">
        <div className="banner">
          <img src={imageUrl} alt="whoweare" />
        </div>
        <div className="banner">
          <p>Biography</p>
          <h3>Who We Are</h3>
          <p>
          In today's fast-paced world, access to timely and reliable medical advice is crucial. Many individuals, especially in rural areas, struggle with language barriers and limited access to healthcare professionals. Urgent cases often require immediate assistance, but traditional systems can be slow and inefficient.

Our AI-Powered Healthcare Assistant is designed to bridge this gap. Using Twilio Voice API and Google Gemini AI, we have created an intelligent, voice-based medical assistant that allows users to simply call a number and describe their symptoms in English or Hindi. The AI then analyzes symptoms, asks relevant medical questions, and suggests appropriate actions—whether it's home remedies or booking a doctor’s appointment for serious conditions.


          </p>
          
          
          
        </div>
      </div>
    </>
  );
};

export default Biography;
