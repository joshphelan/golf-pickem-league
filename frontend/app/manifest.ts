import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Golf Pickem League',
    short_name: 'Golf Pickem',
    start_url: '/',
    display: 'standalone',
    theme_color: '#006747',
    background_color: '#fffef7',
  }
}
