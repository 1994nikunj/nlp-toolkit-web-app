const inputField = document.getElementById("input_file");
const browseButton = document.getElementById("input_browse_button");

// Add a click event listener to the browse button
browseButton.addEventListener("click", () => {
  // Create a file input element
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = ".txt"; // Allow only txt files to be selected

  // Add a change event listener to the file input element
  fileInput.addEventListener("change", () => {
    // Set the input field value to the selected file path
    inputField.value = fileInput.value;
  });

  // Click the file input element to trigger the file selection dialog
  fileInput.click();
});