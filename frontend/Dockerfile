FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./
COPY packages/shared/package.json ./packages/shared/
COPY packages/client-portal/package.json ./packages/client-portal/

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source
COPY . .

# Build
RUN yarn build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/packages/client-portal/.next ./packages/client-portal/.next
COPY --from=builder /app/packages/client-portal/public ./packages/client-portal/public
COPY --from=builder /app/packages/client-portal/package.json ./packages/client-portal/

USER nextjs

EXPOSE 3000

CMD ["yarn", "workspace", "@eranos/client-portal", "start"]
