import { app } from './config/expressConfig.js';
import dotenv from 'dotenv';

dotenv.config();

app.listen(Number(process.env.API_PORT), () => {
    console.log(`Servidor hosteado na porta ${process.env.API_PORT}`);
});
