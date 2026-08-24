const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  try {
    await prisma.$connect();
    console.log('Connected!');
  } catch (e) {
    console.error('Connect failed:', e.message);
  } finally {
    await prisma.$disconnect();
  }
}

main();
