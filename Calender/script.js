const monthYear = document.getElementById("monthYear");
const fullDate = document.getElementById("fullDate");
const daysContainer = document.getElementById("days");

let currentDate = new Date();
let selectedDate = new Date();

const monthNames = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const eventDates = [5, 12, 18, 25];

function renderCalendar() {
  daysContainer.innerHTML = "";

  let year = currentDate.getFullYear();
  let month = currentDate.getMonth();

  monthYear.innerText = `${monthNames[month]} ${year}`;
  fullDate.innerText = selectedDate.toDateString();

  let firstDay = new Date(year, month, 1).getDay();
  let lastDate = new Date(year, month + 1, 0).getDate();
  let prevLastDate = new Date(year, month, 0).getDate();

  for (let i = firstDay; i > 0; i--) {
    createDay(prevLastDate - i + 1, true);
  }

  for (let i = 1; i <= lastDate; i++) {
    createDay(i, false);
  }

  let totalCells = daysContainer.children.length;
  let nextDays = 42 - totalCells;

  for (let i = 1; i <= nextDays; i++) {
    createDay(i, true);
  }
}

function createDay(dayNumber, isOtherMonth) {
  const div = document.createElement("div");
  div.className = "day";
  div.innerText = dayNumber;

  const today = new Date();
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  if (isOtherMonth) {
    div.classList.add("other-month");
  }

  if (
    !isOtherMonth &&
    dayNumber === today.getDate() &&
    month === today.getMonth() &&
    year === today.getFullYear()
  ) {
    div.classList.add("today");
  }

  if (
    !isOtherMonth &&
    dayNumber === selectedDate.getDate() &&
    month === selectedDate.getMonth() &&
    year === selectedDate.getFullYear()
  ) {
    div.classList.add("selected");
  }

  if (!isOtherMonth && eventDates.includes(dayNumber)) {
    div.classList.add("event");
  }

  div.onclick = function () {
    if (!isOtherMonth) {
      selectedDate = new Date(year, month, dayNumber);
      renderCalendar();
    }
  };

  daysContainer.appendChild(div);
}

function prevMonth() {
  currentDate.setMonth(currentDate.getMonth() - 1);
  renderCalendar();
}

function nextMonth() {
  currentDate.setMonth(currentDate.getMonth() + 1);
  renderCalendar();
}

function prevYear() {
  currentDate.setFullYear(currentDate.getFullYear() - 1);
  renderCalendar();
}

function nextYear() {
  currentDate.setFullYear(currentDate.getFullYear() + 1);
  renderCalendar();
}

function goToday() {
  currentDate = new Date();
  selectedDate = new Date();
  renderCalendar();
}

renderCalendar();
