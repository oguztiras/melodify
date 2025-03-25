document.addEventListener("DOMContentLoaded", function () {
    const messageForm = document.querySelector("#messageForm");
    const reviewForm = document.querySelector("#reviewForm");
    const reviewsContainer = document.querySelector("#reviewsContainer");
    const avrRatingElement = document.querySelector("#avrRating");
    let editReviewBtn = document.querySelector("#editReviewBtn");

    messageForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const receiver = document.querySelector("#messageReceiver").value;
        const message = document.querySelector("#message").value;
        const responseElement = document.querySelector("#messageResponse");

        fetch("send_msg", {
            method: "POST",
            body: JSON.stringify({
                receiver: receiver,
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.log(data.error);
                return;
            } else {
                messageForm.style.animationPlayState = "running";
                messageForm.addEventListener("animationend", () => {
                    messageForm.remove();
                    responseElement.innerHTML = data.message;
                });
            }

        })
        .catch(error => console.log("Error:", error));
    });

    if(reviewForm) {
        reviewForm.addEventListener("submit", function(event) {
            event.preventDefault();

            const instructorProfileId = document.querySelector("#instructorProfileId").value;
            const comment = document.querySelector("#comment").value;
            const rating = document.querySelector("#rating").value;

            fetch("review", {
                method: "POST",
                body: JSON.stringify({
                    instructorProfileId: instructorProfileId,
                    comment: comment,
                    rating: rating
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.log(data.error);
                    return;
                } else {
                    reviewForm.style.animationPlayState = "running";
                    reviewForm.addEventListener("animationend", () => {
                        reviewForm.remove();

                        const newReviewElement = document.createElement("div");
                        newReviewElement.classList.add("container", "mb-2", "border-bottom", "border-1", "pb-3");
                        newReviewElement.setAttribute("data-review-id", data.reviewId);
                        newReviewElement.innerHTML = `
                            <div>Reviwer: ${data.reviewer}</div>
                            <div class="reviewComment">Comment: ${data.comment}</div>
                            <div class="reviewRating">Rating: ${data.rating}</div>
                            <button class="btn btn-secondary" id="editReviewBtn">edit</button>
                        `;
                        reviewsContainer.prepend(newReviewElement);

                        avrRatingElement.innerHTML = `Average Rating: ${data.avrRating.toFixed(2)}`;

                        editReviewBtn = document.querySelector("#editReviewBtn");
                        editReview();
                    });
                }
            })
            .catch(error => console.log("Error:", error));
        });
    }

    if (editReviewBtn) {
        editReview();
    }

    function editReview() {
        editReviewBtn.addEventListener("click", function() {
            const reviewId = this.parentElement.dataset.reviewId;
            
            const ratingElement = this.parentElement.querySelector(".reviewRating");
            const commentElement = this.parentElement.querySelector(".reviewComment");
            const existingRating = ratingElement.innerHTML.replace("Rating: ", "");
            const existingComment = commentElement.innerHTML.replace("Comment: ", "");
            ratingElement.innerHTML = "";
            commentElement.innerHTML = "";

            const editForm = document.createElement("form");
            editForm.id = "editReviewForm";
            editForm.innerHTML = `
                <textarea class="form-control" name="editedComment" id="editedComment" rows="5" required>${existingComment}</textarea>
                <select class="form-control" name="editedRating" id="editedRating" required>
                    <option value="${existingRating}" selected>${existingRating}</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                </select>
                <button class="btn btn-secondary" type="submit">Save Edit</button>
            `;
            this.parentElement.insertBefore(editForm, this);
            this.style.display = "none";

            editForm.addEventListener("submit", function(event) {
                event.preventDefault();
                
                const editedComment = document.querySelector("#editedComment").value;
                const editedRating = document.querySelector("#editedRating").value;

                fetch("editReview", {
                    method: "PUT",
                    body: JSON.stringify({
                        reviewId: reviewId,
                        editedComment: editedComment,
                        editedRating: editedRating
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.log(data.error);
                        return;
                    } else {
                        editForm.innerHTML = "";
                        ratingElement.innerHTML = `Rating: ${data.editedRating}`;
                        commentElement.innerHTML = `Comment: ${data.editedComment}`;
                        avrRatingElement.innerHTML = `Average Rating: ${data.avrRating.toFixed(2)}`;
                        editReviewBtn.style.display = "inline-block";
                    }
                })
                .catch(error => console.log("Error:", error));
            });
        });
    }

});