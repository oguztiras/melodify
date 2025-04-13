document.addEventListener("DOMContentLoaded", function () {
    form = document.querySelector("#searchForm");
    profiles_container = document.querySelector("#profiles_container");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const city = document.querySelector("#city").value;
        const level = document.querySelector("#level").value;

        fetch(`search?city=${city}&level=${level}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.log(data.error);
                return;
            } else {
                profiles_container.innerHTML = "";

                data.profiles.forEach(profile => {
                    const profileElement = document.createElement("div");
                    profileElement.classList.add("container", "mb-5");
                    profileElement.innerHTML = `
                        <h3>
                            <a href="${profile.id}" class="text-decoration-none text-capitalize">${profile.username}</a>
                        </h3>
                        <div>${profile.bio.slice(0, 200)}...</div>
                        <div class="fw-semibold text-capitalize">${profile.city}</div>
                        <div class="fw-semibold text-capitalize">${profile.level}</div>
                    `;
                    profiles_container.appendChild(profileElement)
                });
            }
        })
        .catch(error => console.log("Error:", error));
    });

});