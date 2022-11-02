window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

console.log("from script");
console.log (document.getElementById("delete"))
deleteBtn = document.getElementById("delete")
deleteBtn.onclick = function(e) {
  console.log("Delete event: ", e);
  const todoId = deleteBtn.dataset.id;
  fetch('/venues/'+ todoId ,{
      method: 'DELETE'
  })
  };
