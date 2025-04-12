import React from "react";

const AppointmentDetails = ({ details }) => {
  return (
    <div style={styles.box}>
      <h2>Booked Appointment</h2>
      <p><strong>Patient Name:</strong> {details.name}</p>
      <p><strong>Doctor:</strong> {details.doctor}</p>
      <p><strong>Time:</strong> {details.time}</p>
      <p><strong>Date:</strong> {details.date}</p>
    </div>
  );
};

const styles = {
  box: {
    border: "1px solid #ddd",
    padding: "20px",
    borderRadius: "8px",
    backgroundColor: "#f9f9f9",
    marginTop: "20px",
    boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.1)",
    maxWidth: "600px",
    marginLeft: "auto",
    marginRight: "auto",
  }
};

export default AppointmentDetails;
