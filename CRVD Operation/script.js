const nameInput = document.getElementById("name-input");
const ageInput = document.getElementById("age-input");
const countryInput = document.getElementById("country-input");
const emailInput = document.getElementById("email-input");
const addBtn = document.getElementById("add-btn");

const tableBody = document.getElementById("table-body");

const updateContainer = document.getElementById("update-container");
const updateNameInput = document.getElementById("update-name-input");
const updateAgeInput = document.getElementById("update-age-input");
const updateCountryInput = document.getElementById("update-country-input");
const updateEmailInput = document.getElementById("update-email-input");
const updateBtn = document.getElementById("update-btn");
const cancelBtn = document.getElementById("cancel-btn");

let students = JSON.parse(localStorage.getItem("students")) || [];
let currentRollNo = null;

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function saveStudents() {
  localStorage.setItem("students", JSON.stringify(students));
}

function renderTable() {
  tableBody.innerHTML = "";

  students.forEach(student => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${student.rollno}</td>
      <td>${student.name}</td>
      <td>${student.age}</td>
      <td>${student.country}</td>
      <td>${student.email}</td>
      <td>
        <button class="edit-btn" onclick="showUpdateForm(${student.rollno})">編集 / EDIT</button>
        <button class="delete-btn" onclick="deleteStudent(${student.rollno})">削除 / DELETE</button>
      </td>
    `;

    tableBody.appendChild(row);
  });
}

function addStudent() {
  const name = nameInput.value.trim().toUpperCase();
  const age = ageInput.value.trim();
  const country = countryInput.value;
  const email = emailInput.value.trim().toUpperCase();

  if (name === "") {
    alert("氏名を入力してください / ENTER NAME");
    return;
  }

  if (age === "" || age <= 0) {
    alert("正しい年齢を入力してください / ENTER VALID AGE");
    return;
  }

  if (country === "") {
    alert("国籍を選択してください / SELECT COUNTRY");
    return;
  }

  if (!emailRegex.test(email)) {
    alert("正しいメールアドレスを入力してください / ENTER VALID EMAIL");
    return;
  }

  const rollno = students.length > 0
    ? Math.max(...students.map(s => s.rollno)) + 1
    : 1;

  students.push({
    rollno,
    name,
    age,
    country,
    email
  });

  saveStudents();
  renderTable();

  nameInput.value = "";
  ageInput.value = "";
  countryInput.selectedIndex = 0;
  emailInput.value = "";
}

function showUpdateForm(rollno) {
  const student = students.find(student => student.rollno === rollno);

  if (student) {
    updateNameInput.value = student.name;
    updateAgeInput.value = student.age;
    updateCountryInput.value = student.country;
    updateEmailInput.value = student.email;
    currentRollNo = student.rollno;
    updateContainer.style.display = "block";
  }
}

function updateStudent() {
  const name = updateNameInput.value.trim().toUpperCase();
  const age = updateAgeInput.value.trim();
  const country = updateCountryInput.value;
  const email = updateEmailInput.value.trim().toUpperCase();

  if (name === "") {
    alert("氏名を入力してください / ENTER NAME");
    return;
  }

  if (age === "" || age <= 0) {
    alert("正しい年齢を入力してください / ENTER VALID AGE");
    return;
  }

  if (country === "") {
    alert("国籍を選択してください / SELECT COUNTRY");
    return;
  }

  if (!emailRegex.test(email)) {
    alert("正しいメールアドレスを入力してください / ENTER VALID EMAIL");
    return;
  }

  const student = students.find(student => student.rollno === currentRollNo);

  if (student) {
    student.name = name;
    student.age = age;
    student.country = country;
    student.email = email;

    saveStudents();
    renderTable();
    hideUpdateForm();
  }
}

function hideUpdateForm() {
  updateNameInput.value = "";
  updateAgeInput.value = "";
  updateCountryInput.selectedIndex = 0;
  updateEmailInput.value = "";
  currentRollNo = null;
  updateContainer.style.display = "none";
}

function deleteStudent(rollno) {
  if (confirm("この学生を削除しますか？ / DELETE THIS STUDENT?")) {
    students = students.filter(student => student.rollno !== rollno);
    saveStudents();
    renderTable();
    hideUpdateForm();
  }
}

addBtn.addEventListener("click", addStudent);
updateBtn.addEventListener("click", updateStudent);
cancelBtn.addEventListener("click", hideUpdateForm);

renderTable();