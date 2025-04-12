import React from "react";
import Hero from "../components/Hero";
import AppointmentForm from "../components/AppointmentForm";
import AppointmentDetails from "../components/AppointmentDetails";

const Appointment = () => {
  const appointmentDetails = {
    name: "John Doe",
    doctor: "Dr. Smith",
    time: "10:00 AM",
    date: "March 29, 2025",
  };

  return (
    <>
      <Hero
        title={"Schedule Your Appointment | ZeeCare Medical Institute"}
        imageUrl={"/signin.png"}
      />
      <AppointmentDetails details={appointmentDetails} />
      <AppointmentForm />
    </>
  );
};

export default Appointment;
