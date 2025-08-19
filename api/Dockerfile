# Stage 1: Build the Go binary
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY go.mod ./
COPY go.sum ./
COPY . .
# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -v -o /fiso_server ./cmd/fiso_server/main.go

# Stage 2: Create the final small image
FROM alpine:latest
WORKDIR /root/
# Copy the binary from the builder stage
COPY --from=builder /fiso_server .
# Expose port 8080
EXPOSE 8080
# Command to run the executable
CMD ["./fiso_server"]