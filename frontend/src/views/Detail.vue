<template>
    <v-container>
        <v-row>
            <v-col cols="12" md="4">
                <v-img :src="product.imgPath" class="img" height="350px"></v-img>
                <h3 class="headline">{{ product.name }}</h3>
            </v-col>

            <v-col cols="12" md="8">
                <p v-for="(content, index) in product.desc" :key="index">{{ content }}</p>
            </v-col>
        </v-row>

        <v-row>
            <v-col cols="12">
                <p v-if="fileContent" v-html="formattedFileContent"></p>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            product: {},
            fileContent: "", // Biến lưu nội dung file .txt
        };
    },
    computed: {
        formattedFileContent() {
            return this.fileContent.replace(/\n/g, '<br>'); // Thay thế ký tự xuống dòng bằng <br>
        }
    },
    created() {
        const productId = this.$route.params.id;
        axios.get('/data.json')
            .then(response => {
                const products = response.data;
                this.product = products.find(p => p.id === parseInt(productId));
                this.loadFile(this.product.recipe); // Gọi hàm tải nội dung file .txt
            })
            .catch(error => {
                console.error("Lỗi khi tải dữ liệu:", error);
            });
    },
    methods: {
        async loadFile(filePath) {
            try {
                const response = await axios.get(filePath); // Đường dẫn tới file .txt
                this.fileContent = response.data; // Lưu nội dung file vào biến fileContent
            } catch (error) {
                console.error("Lỗi khi tải file:", error);
            }
        },
    },
};
</script>

<style scoped>
.headline {
    text-align: center;
}

p {
    text-align: justify;
    margin-bottom: .5rem;
}
</style>
