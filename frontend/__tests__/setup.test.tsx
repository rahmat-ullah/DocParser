import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Simple test to verify Jest setup is working
describe('Setup Test', () => {
  it('should render basic element', () => {
    render(<div>Test Setup</div>)
    expect(screen.getByText('Test Setup')).toBeInTheDocument()
  })

  it('should pass basic assertion', () => {
    expect(true).toBe(true)
  })
})
