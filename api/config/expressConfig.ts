import express, { Express } from 'express';
import cors, { CorsOptions } from 'cors';
import dotenv from 'dotenv';
import searchRouter from '../src/controllers/search_controller.js'
import researchersByTagRouter from '../src/controllers/get_researchers_by_tag.js'

dotenv.config();

export const app: Express = express();


const options: CorsOptions = {
    credentials: true,
    origin: '*'
};

app.use(cors(options));
app.use(express.json());
app.use(
    express.urlencoded({
        extended: true,
    }),
);

app.use('/api/search', searchRouter);
app.use('/api/researchers', researchersByTagRouter);
