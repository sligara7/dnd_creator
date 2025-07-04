console.log("Testing character creation function"); 
function testAPI() {
  console.log("Calling startCreation...");
  if (typeof startCreation === "function") {
    console.log("startCreation function exists");
  } else {
    console.log("startCreation function NOT found");
  }
}
testAPI();
