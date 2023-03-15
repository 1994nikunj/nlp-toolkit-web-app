var dropdown = document.getElementsByClassName('dropdown-btn');
var tabcontent_dev = document.getElementsByClassName('tabcontent_2');
var tabcontent_cat = document.getElementsByClassName('tabcontent');

this.deviceName = '001';
this.categoryName = 'RPHY';
this.id = this.categoryName + '_' + this.deviceName;

if (localStorage.getItem('deviceName') != null & localStorage.getItem('categoryName') != null) {
	getInfo('back')
}

for (var i = 0; i < dropdown.length; i++) {
	dropdown[i].addEventListener('click', function () {
		console.log('Click caught!')
		this.classList.toggle('active');
		var dropdownContent = this.nextElementSibling;
		if (dropdownContent.style.display === 'block') {
			dropdownContent.style.display = 'none';
		} else {
			dropdownContent.style.display = 'block';
		}
	});
}

function openCategory(category) {
	this.categoryName = category;
	for (var i = 0; i < tabcontent_cat.length; i++) {
		tabcontent_cat[i].style.display = 'none';
	}
	setContentBorder(this.categoryName)
	getInfo('next');
}

function setContentBorder(categeogryId) {
	document.getElementById(categeogryId).style.display = 'block';
	document.getElementById(categeogryId).style.boxShadow = '0px 0px 5px rgb(0, 90, 81)';
	document.getElementById(categeogryId).style.borderRadius = '7px';
}
function openDevice(device) {
	this.deviceName = device;
	for (var i = 0; i < tabcontent_dev.length; i++) {
		tabcontent_dev[i].style.display = 'none';
	}
	getInfo('next');
}

function getInfo(flag) {
	if (flag == 'next') {
		this.id = this.categoryName + '_' + this.deviceName;
		document.getElementById(this.id).style.display = 'block';
		localStorage.setItem("deviceName", this.deviceName);
		localStorage.setItem("categoryName", this.categoryName);
		document.getElementById("devID").innerHTML = this.deviceName;
		document.getElementById("catName").innerHTML = this.categoryName;
	}
	if (flag == 'back') {
		devName = localStorage.getItem('deviceName');
		catName = localStorage.getItem('categoryName');
		id = catName + '_' + devName;
		setContentBorder(catName)
		document.getElementById(id).style.display = 'block';
		document.getElementById("devID").innerHTML = devName;
		document.getElementById("catName").innerHTML = catName;
	}
}
