import { useParams } from 'react-router-dom';
import Band from '../components/Band.jsx';
import Header from '../components/Header.jsx';
import Hero from '../components/Hero.jsx';
import Topics from '../components/Topics.jsx';
import Services from '../components/Services.jsx';
import About from '../components/About.jsx';
import Reviews from '../components/Reviews.jsx';
import Cta from '../components/Cta.jsx';
import Footer from '../components/Footer.jsx';
import { images } from '../content/images.js';
import './LandingPage.css';

export default function LandingPage() {
  const { variant } = useParams();
  const media = variant === 'full' ? images : null;

  return (
    <div className={`page theme-${variant}`}>
      <Band variant={variant}>
        <Header variant={variant} />
        <div className="divider" />
        <Hero image={media?.hero} />
        <div className="divider" />
        <Topics images={media} />
        <div className="divider" />
        <Services />
        <div className="divider" />
        <About image={media?.about} />
        <div className="divider" />
        <Reviews images={media} />
        <div className="divider" />
        <Cta />
        <div className="divider" />
        <Footer variant={variant} />
      </Band>
    </div>
  );
}
