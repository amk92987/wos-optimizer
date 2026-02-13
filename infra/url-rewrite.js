function handler(event) {
  var request = event.request;
  var uri = request.uri;

  // Root path - serve index.html
  if (uri === '/') {
    return request;
  }

  // API requests - pass through
  if (uri.startsWith('/api/')) {
    return request;
  }

  // Static assets - pass through
  if (uri.startsWith('/_next/') || uri.startsWith('/icons/') || uri.startsWith('/images/') || uri.indexOf('.') !== -1) {
    return request;
  }

  // Strip trailing slash
  if (uri.endsWith('/')) {
    uri = uri.slice(0, -1);
  }

  // Append .html for route paths
  request.uri = uri + '.html';
  return request;
}
