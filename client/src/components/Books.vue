<template>
    <div class="container">
        <div class="row">
            <div class="col-sm-10">
                <h1>Books</h1>
                <hr><br><br>

                <alert :message="message" v-if='showMessage'></alert>

                <!-- Login button if not logged in, else show the Add Book button -->
                <button
                    v-if="!isAdmin"
                    type="button"
                    class="btn btn-primary btn-sm"
                    @click="toggleLoginModal">
                    Admin Login
                </button>

                <button
                    v-if="isAdmin"
                    type="button"
                    class="btn btn-success btn-sm"
                    @click="toggleAddBookModal">
                    Add Book
                </button>
                
                <br><br>

                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Title</th>
                            <th scope="col">Author</th>
                            <th scope="col">Read?</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(book, index) in books" :key="index">
                            <td>{{ book.title }}</td>
                            <td>{{ book.author }}</td>
                            <td>
                                <span v-if="book.read">Yes</span>
                                <span v-else>No</span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <!-- Show Update/Delete buttons only for admin -->
                                    <button
                                        v-if="isAdmin"
                                        type="button"
                                        class="btn btn-warning btn-sm"
                                        @click="toggleEditBookModal(book)">
                                        Update
                                    </button>
                                    <button
                                        v-if="isAdmin"
                                        type="button"
                                        class="btn btn-danger btn-sm"
                                        @click="handleDeleteBook(book)">
                                        Delete
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Add New Book Modal -->
    <div
        ref="addBookModal"
        class="modal fade"
        :class="{ show: activeAddBookModal, 'd-block': activeAddBookModal }"
        tabindex="-1"
        role="dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add a new book</h5>
                    <button
                        type="button"
                        class="close"
                        data-dismiss="modal"
                        aria-label="Close"
                        @click="toggleAddBookModal">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form>
                        <div class="mb-3">
                            <label for="addBookTitle" class="form-label">Title:</label>
                            <input
                                type="text"
                                class="form-control"
                                id="addBookTitle"
                                v-model="addBookForm.title"
                                placeholder="Enter title">
                        </div>
                        <div class="mb-3">
                            <label for="addBookAuthor" class="form-label">Author:</label>
                            <input
                                type="text"
                                class="form-control"
                                id="addBookAuthor"
                                v-model="addBookForm.author"
                                placeholder="Enter author">
                        </div>
                        <div class="mb-3 form-check">
                            <input
                                type="checkbox"
                                class="form-check-input"
                                id="addBookRead"
                                v-model="addBookForm.read">
                            <label class="form-check-label" for="addBookRead">Read?</label>
                        </div>
                        <div class="btn-group" role="group">
                            <button
                                type="button"
                                class="btn btn-primary btn-sm"
                                @click="handleAddSubmit">
                                Submit
                            </button>
                            <button
                                type="button"
                                class="btn btn-danger btn-sm"
                                @click="handleAddReset">
                                Reset
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div v-if="activeAddBookModal" class="modal-backdrop fade show"></div>

    <!-- Edit Book Modal -->
    <div
        ref="editBookModal"
        class="modal fade"
        :class="{ show: activeEditBookModal, 'd-block': activeEditBookModal }"
        tabindex="-1"
        role="dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Update</h5>
                    <button
                        type="button"
                        class="close"
                        data-dismiss="modal"
                        aria-label="Close"
                        @click="toggleEditBookModal">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form>
                        <div class="mb-3">
                            <label for="editBookTitle" class="form-label">Title:</label>
                            <input
                                type="text"
                                class="form-control"
                                id="editBookTitle"
                                v-model="editBookForm.title"
                                placeholder="Enter title">
                        </div>
                        <div class="mb-3">
                            <label for="editBookAuthor" class="form-label">Author:</label>
                            <input
                                type="text"
                                class="form-control"
                                id="editBookAuthor"
                                v-model="editBookForm.author"
                                placeholder="Enter author">
                        </div>
                        <div class="mb-3 form-check">
                            <input
                                type="checkbox"
                                class="form-check-input"
                                id="editBookRead"
                                v-model="editBookForm.read">
                            <label class="form-check-label" for="editBookRead">Read?</label>
                        </div>
                        <div class="btn-group" role="group">
                            <button
                                type="button"
                                class="btn btn-primary btn-sm"
                                @click="handleEditSubmit">
                                Submit
                            </button>
                            <button
                                type="button"
                                class="btn btn-danger btn-sm"
                                @click="handleEditCancel">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div v-if="activeEditBookModal" class="modal-backdrop fade show"></div>

    <!-- Login Modal -->
    <div
        ref="loginModal"
        class="modal fade"
        :class="{ show: activeLoginModal, 'd-block': activeLoginModal }"
        tabindex="-1"
        role="dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Admin Login</h5>
                    <button
                        type="button"
                        class="close"
                        data-dismiss="modal"
                        aria-label="Close"
                        @click="toggleLoginModal">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="handleLoginSubmit">
                        <div class="mb-3">
                            <label for="adminUsername" class="form-label">Username:</label>
                            <input
                                type="text"
                                class="form-control"
                                id="adminUsername"
                                v-model="loginForm.username"
                                placeholder="Enter admin username">
                        </div>
                        <div class="mb-3">
                            <label for="adminPassword" class="form-label">Password:</label>
                            <input
                                type="password"
                                class="form-control"
                                id="adminPassword"
                                v-model="loginForm.password"
                                placeholder="Enter admin password">
                        </div>
                        <div class="btn-group" role="group">
                            <button
                                type="submit"
                                class="btn btn-primary btn-sm">
                                Login
                            </button>
                            <button
                                type="button"
                                class="btn btn-danger btn-sm"
                                @click="toggleLoginModal">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div v-if="activeLoginModal" class="modal-backdrop fade show"></div>
</template>


<script>
import axios from 'axios';
import Alert from './Alert.vue';


export default {
    data() {
        return {
            activeAddBookModal: false,
            activeEditBookModal: false,
            activeLoginModal: false,
            isAdmin: false, // Admin status
            loginForm: {
                username: '',
                password: ''
            },
            token: null, // Store the JWT token
            addBookForm: {
                title: '',
                author: '',
                read: false,
            },
            books: [],
            message: '',
            showMessage: false,
            editBookForm: {
                id: '',
                title: '',
                author: '',
                read: false,
            },
        };
    },
    components: {
        alert: Alert,
    },
    methods: {
        addBook(payload) {
            if (!this.isAdmin) {
                this.message = "Only admins can add books!";
                this.showMessage = true;
                return;
            }
            const path = 'http://ec2-3-137-151-250.us-east-2.compute.amazonaws.com/books';
            axios.post(path, payload, { headers: { Authorization: this.token } })
                .then(() => {
                    this.getBooks();
                    this.message = 'Book Added!';
                    this.showMessage = true;
                })
                .catch((error) => {
                    console.log(error);
                    this.getBooks();
                });
        },
        getBooks() {
            const path = 'http://ec2-3-137-151-250.us-east-2.compute.amazonaws.com/books';
            axios.get(path)
                .then((res) => {
                    this.books = res.data.books;
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        handleAddReset() {
            this.initForm();
        },
        handleAddSubmit() {
            this.toggleAddBookModal();
            const payload = { ...this.addBookForm };
            this.addBook(payload);
            this.initForm();
        },
        initForm() {
            this.addBookForm.title = '';
            this.addBookForm.author = '';
            this.addBookForm.read = false;
            this.editBookForm.id = '';
            this.editBookForm.title = '';
            this.editBookForm.author = '';
            this.editBookForm.read = false;
        },
        toggleAddBookModal() {
            const body = document.querySelector('body');
            this.activeAddBookModal = !this.activeAddBookModal;
            if (this.activeAddBookModal) {
                body.classList.add('modal-open');
            } else {
                body.classList.remove('modal-open');
            }
        },
        toggleEditBookModal(book) {
            if (book) {
                this.editBookForm = { ...book };
            }
            const body = document.querySelector('body');
            this.activeEditBookModal = !this.activeEditBookModal;
            if (this.activeEditBookModal) {
                body.classList.add('modal-open');
            } else {
                body.classList.remove('modal-open');
            }
        },
        handleEditSubmit() {
            this.toggleEditBookModal(null);
            const payload = { ...this.editBookForm };
            this.updateBook(payload, this.editBookForm.id);
        },
        updateBook(payload, bookID) {
            if (!this.isAdmin) {
                this.message = "Only admins can update books!";
                this.showMessage = true;
                return;
            }
            const path = `http://ec2-3-137-151-250.us-east-2.compute.amazonaws.com/books/${bookID}`;
            axios.put(path, payload, { headers: { Authorization: this.token } })
                .then(() => {
                    this.getBooks();
                    this.message = 'Book updated!';
                    this.showMessage = true;
                })
                .catch((error) => {
                    console.error(error);
                    this.getBooks();
                });
        },
        handleEditCancel() {
            this.toggleEditBookModal(null);
            this.initForm();
            this.getBooks();
        },
        handleDeleteBook(book) {
            if (!this.isAdmin) {
                this.message = "Only admins can delete books!";
                this.showMessage = true;
                return;
            }
            this.removeBook(book.id);
        },
        removeBook(bookID) {
            const path = `http://ec2-3-137-151-250.us-east-2.compute.amazonaws.com/books/${bookID}`;
            axios.delete(path, { headers: { Authorization: this.token } })
                .then(() => {
                    this.getBooks();
                    this.message = 'Book removed!';
                    this.showMessage = true;
                })
                .catch((error) => {
                    console.error(error);
                    this.getBooks();
                });
        },
        toggleLoginModal() {
            const body = document.querySelector('body');
            this.activeLoginModal = !this.activeLoginModal;
            if (this.activeLoginModal) {
                body.classList.add('modal-open');
            } else {
                body.classList.remove('modal-open');
            }
        },
        handleLoginSubmit() {
            const { username, password } = this.loginForm;
            const payload = { username, password };

            axios.post('http://ec2-3-137-151-250.us-east-2.compute.amazonaws.com/login', payload)
                .then((response) => {
                    if (response.data.token) {
                        this.token = response.data.token;
                        this.isAdmin = true;
                        this.message = 'Logged in successfully as Admin';
                        this.showMessage = true;
                    } else {
                        this.message = 'Login failed';
                        this.showMessage = true;
                    }
                })
                .catch((error) => {
                    this.message = 'Login failed';
                    this.showMessage = true;
                    console.error(error);
                });

            this.toggleLoginModal();
        }
    },
    created() {
        this.getBooks();
    },
};
</script>
