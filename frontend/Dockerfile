FROM node:18-alpine

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build for production
RUN npm run build

# Expose port
EXPOSE 5173

# Start development server (for dev) or preview (for production)
CMD ["npm", "run", "preview", "--", "--host", "--port", "5173"]
