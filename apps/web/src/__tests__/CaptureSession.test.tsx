
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CaptureSession from '../components/CaptureSession';

test('renders CaptureSession root element', () => {
  render(<CaptureSession />);
  const root = screen.getByTestId('capture-session');
  expect(root).toBeInTheDocument();
});
