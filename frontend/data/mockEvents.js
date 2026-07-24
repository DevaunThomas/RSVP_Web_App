function getFutureDate(daysFromToday) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromToday);

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

// Temp event data used until the frontend is connected to the API
export const mockEvents = [
  {
    id: 1,
    title: "Fall Student Organization Fair",
    description:
      "Meet student organizations, explore campus involvement opportunities, and connect with other students.",
    date: getFutureDate(3),
    startTime: "11:00",
    endTime: "14:00",
    location: "University Center",
    organizer: "Office for Student Life",
    capacity: 200,
    rsvpCount: 146,
    status: "open",
  },
  {
    id: 2,
    title: "Career Services Resume Workshop",
    description:
      "Learn how to strengthen your resume and prepare it for internships and job applications.",
    date: getFutureDate(6),
    startTime: "15:00",
    endTime: "16:30",
    location: "Fairlane Center North",
    organizer: "Career Services",
    capacity: 50,
    rsvpCount: 47,
    status: "open",
  },
  {
    id: 3,
    title: "Campus Movie Night",
    description:
      "Enjoy a free movie screening with snacks and refreshments provided for attendees.",
    date: getFutureDate(9),
    startTime: "19:00",
    endTime: "21:30",
    location: "Kochoff Hall",
    organizer: "Student Government",
    capacity: 120,
    rsvpCount: 120,
    status: "full",
  },
  {
    id: 4,
    title: "Engineering Club Project Showcase",
    description:
      "View student engineering projects and speak with the teams behind each design.",
    date: getFutureDate(12),
    startTime: "13:00",
    endTime: "16:00",
    location: "Engineering Laboratory Building",
    organizer: "Engineering Club",
    capacity: 90,
    rsvpCount: 58,
    status: "open",
  },
  {
    id: 5,
    title: "Wellness Wednesday",
    description:
      "Take a break with guided activities focused on stress management and student wellness.",
    date: getFutureDate(15),
    startTime: "12:00",
    endTime: "14:00",
    location: "University Center Patio",
    organizer: "Counseling and Psychological Services",
    capacity: 75,
    rsvpCount: 31,
    status: "open",
  },
  {
    id: 6,
    title: "International Student Social",
    description:
      "Connect with students from around the world through games, conversation, and refreshments.",
    date: getFutureDate(18),
    startTime: "17:00",
    endTime: "19:00",
    location: "Renick University Center",
    organizer: "International Affairs",
    capacity: 80,
    rsvpCount: 64,
    status: "open",
  },
];