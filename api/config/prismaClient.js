"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var client_1 = require("@prisma/client");
var prisma_extension_random_1 = require("prisma-extension-random");
var prisma = new client_1.PrismaClient().$extends((0, prisma_extension_random_1.default)());
exports.default = prisma;
