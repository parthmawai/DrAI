import React, { useState } from "react";
import Hero from "../components/Hero";
import Biography from "../components/Biography";
import MessageForm from "../components/MessageForm";
import Departments from "../components/Departments";
import axios from "axios";

const Home = () => {
  const [phoneNumber, setPhoneNumber] = useState("");

  const handleCall = async () => {
    if (!phoneNumber) {
      alert("Please enter a phone number");
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5001/make_call", {
        to_number: phoneNumber
      });
      alert(response.data.message);
    } catch (error) {
      alert("Error: " + error.response.data.error);
    }
  };

  return (
    <>
      {/* Hero Section with Call Now Button */}
      <div className="relative">
        <Hero
          title={
            "Welcome to ZeeCare Medical Institute | Your Trusted Healthcare Provider"
          }
          imageUrl={"/hero.png"}
        />
        
        {/* Call Now Section - Positioned Below the Hero Title */}
        <div className="absolute top-2/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-4 p-4 bg-white rounded-lg shadow-lg max-w-md w-full sm:w-auto">
          <h2 className="text-lg font-semibold text-gray-800">Need Assistance? Call Now!</h2>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Enter phone number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="p-2 border rounded-lg text-gray-700 w-40 sm:w-56"
            />
            <button
              onClick={handleCall}
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg shadow-md hover:opacity-80 transition duration-300"
            >
              📞 Call Now
            </button>
          </div>
        </div>
      </div>

      {/* Other Sections */}
      <Biography imageUrl={"/about.png"} />
      <Departments />
      <MessageForm />
    </>
  );
};

export default Home;
