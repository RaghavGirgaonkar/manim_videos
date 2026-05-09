from manim import *
import numpy as np

class TwoElementInterferometer(Scene):
    def construct(self):
        # --- 1. Title Sequence ---
        title = Text("The two-element interferometer", color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        
        # --- 2. Physical Setup ---
        BASELINE = 6
        self.square = Square()
        self.circle = Circle()
        self.circle.set_color(BLUE)
        self.square.set_color(RED)
        
        self.a1 = Line(start=[-BASELINE//2., 0., 0.], end=[-BASELINE//2., 1., 0.])
        self.a2 = Line(start=[BASELINE//2., 0., 0.], end=[BASELINE//2., 1., 0.])
        
        self.ax = NumberLine(
            x_range=[-20, 20], 
            length=96, 
            include_numbers=False
        )

        def create_dish():
            dish = ParametricFunction(
                lambda t: np.array([t, 0.4 * t**2, 0]), 
                t_range=[-0.8, 0.8]
            )
            dish.rotate(-45 * DEGREES, about_point=ORIGIN)
            return dish

        self.dish1 = create_dish()
        self.dish2 = create_dish()

        self.dish1.shift(self.a1.get_end())
        self.dish2.shift(self.a2.get_end())

        self.antennas = VGroup(self.a1, self.a2, self.dish1, self.dish2, self.ax)
        self.antennas.shift(DOWN*2.5)
        
        self.play(Create(self.ax), run_time=1)
        
        self.play(
            Create(self.a1), Create(self.dish1), 
            Create(self.a2), Create(self.dish2), 
            run_time=1
        )
        self.wait(1)

        # --- 3. Wavefronts ---
        wavefronts = VGroup()
        num_waves = 4
        spacing = 2.0 
        wavefront_label = MathTex(r"\text{Plane Wavefronts}", color=BLUE).to_corner(UL)
        
        for i in range(num_waves):
            wave = DashedLine(UP*8, DOWN*8, color=YELLOW)
            wave.rotate(45 * DEGREES)
            start_offset = 10 + (i * spacing)
            wave.move_to(self.a1.get_end() + (UP + RIGHT) * start_offset)
            wavefronts.add(wave)
        
        animations = []
        speed = 4.0 
        
        for i, wave in enumerate(wavefronts):
            travel_distance = 10 + (i * spacing)
            travel_time = travel_distance / speed
            anim = Succession(
                wave.animate(run_time=travel_time, rate_func=linear).shift((DOWN + LEFT) * travel_distance),
                FadeOut(wave, run_time=0.1)
            )
            animations.append(anim)

        self.add(wavefronts)
        baseline_arrow = Arrow(
            start=self.a1.get_end(),
            end=self.a2.get_end(),
            buff=0, color = BLUE
        )
        baseline_label = MathTex(r"\vec{b}", color=BLUE).next_to(baseline_arrow, DOWN, buff=0.1)
        
        self.play(
            AnimationGroup(*animations, lag_ratio=0, run_time=5), 
            Write(wavefront_label),
            Create(baseline_arrow, run_time=1.5),
            Write(baseline_label, run_time=1.5)
        )
        self.wait(0.5)
        self.play(FadeOut(wavefront_label))

        # --- 4. FIRST ZOOM OUT & CIRCUIT DRAWING ---
        observatory = VGroup(self.antennas, baseline_arrow, baseline_label)
        self.play(observatory.animate.scale(0.75).shift(UP * 1.5))
        
        p1 = self.a1.get_start()
        p2 = self.a2.get_start()
        
        y_box = p1[1] - 2.0
        
        box = Rectangle(width=2.8, height=1.0).move_to([0, y_box, 0])
        box_math = MathTex(r"\langle V_1 \ast V_2 \rangle").scale(0.8).move_to(box.get_center())
        box_label = Text("Correlator", font_size=28).next_to(box, RIGHT, buff=0.3)
        correlator = VGroup(box, box_math, box_label)
        
        y_turn = (p1[1] + box.get_top()[1]) / 2
        
        path1 = VMobject().set_points_as_corners([
            p1, [p1[0], y_turn, 0], [-0.5, y_turn, 0], [-0.5, box.get_top()[1], 0]
        ])
        path2 = VMobject().set_points_as_corners([
            p2, [p2[0], y_turn, 0], [0.5, y_turn, 0], [0.5, box.get_top()[1], 0]
        ])
        
        wire1 = path1.copy().set_style(stroke_color=RED, stroke_width=2)
        wire2 = path2.copy().set_style(stroke_color=RED, stroke_width=2)
        
        v1_label = MathTex("V_1").move_to([p1[0] - 0.5, (p1[1] + y_turn)/2, 0])
        v2_label = MathTex("V_2").move_to([p2[0] + 0.5, (p2[1] + y_turn)/2, 0])
        
        self.play(
            Create(wire1), Create(wire2), 
            Create(correlator), 
            Write(v1_label), Write(v2_label)
        )

        # --- 5. CONTINUOUS GLOW DOTS UPDATER ---
        def get_glow_dot():
            glow = VGroup()
            for r in np.linspace(0.03, 0.15, 4):
                glow.add(Dot(radius=r, color=YELLOW, fill_opacity=0.2))
            glow.add(Dot(radius=0.03, color=WHITE))
            return glow

        signal_manager = Mobject()
        signal_manager.time = 0
        signal_manager.last_spawn = 0
        signal_manager.dot_scale = 1.0 # Added to shrink dots during the final zoom
        signal_dots = VGroup()
        self.add(signal_manager, signal_dots)

        def update_signals(mob, dt):
            mob.time += dt
            if mob.time - mob.last_spawn > 1.2:
                # Multiply by our dynamic scale factor
                d1 = get_glow_dot().scale(mob.dot_scale)
                d1.path = wire1 # FIXED: Using the drawn wire instead of the hidden path
                d1.alpha = 0
                
                d2 = get_glow_dot().scale(mob.dot_scale)
                d2.path = wire2 # FIXED: Using the drawn wire instead of the hidden path
                d2.alpha = 0
                
                signal_dots.add(d1, d2)
                mob.last_spawn = mob.time
            
            for d in list(signal_dots):
                d.alpha += 0.4 * dt 
                if d.alpha >= 1:
                    signal_dots.remove(d)
                else:
                    d.move_to(d.path.point_from_proportion(d.alpha))

        signal_manager.add_updater(update_signals)

        # --- 6. GEOMETRY OVERLAY ---
        s0_start = self.a1.get_end()
        s0_dir = (UP + RIGHT) / np.linalg.norm(UP + RIGHT) # Unit vector for 45 degrees
        b_vec = self.a2.get_end() - self.a1.get_end()
        
        # Dot product gives the exact length of the projected baseline
        proj_len = np.dot(b_vec, s0_dir)

        intersection = s0_start + proj_len * s0_dir
        s0_vector = Arrow(start=s0_start, end=s0_start + (UP + RIGHT) * 1.5, buff=0, color=GREEN)
        s0_label = MathTex(r"\hat{s}_0", color=GREEN).next_to(s0_vector.get_end(), UP+LEFT, buff=0.1)
        
        ref_line = DashedLine(start=s0_start, end=s0_start + RIGHT * 1.5, color=GRAY)
        theta_angle = Angle(ref_line, s0_vector, radius=0.6, color=YELLOW)
        theta_label = MathTex(r"\theta", color=YELLOW).move_to(
            Angle(ref_line, s0_vector, radius=1.0).point_from_proportion(0.5)
        )

        # Projected baseline
        s_0_dashed_line = DashedLine(start=s0_start, end=intersection, color=GRAY)
        perp_line = DashedLine(start=self.a2.get_end(), end=intersection, color=GRAY)
        l1 = Line(intersection, s0_start)
        l2 = Line(intersection, self.a2.get_end())
        right_angle = RightAngle(l1, l2, length=0.2, color=WHITE)
        mid_proj = (s0_start + intersection) / 2
        proj_label = MathTex(r"\text{Projected Baseline } b\sin \theta", font_size=24, color=YELLOW)
        proj_label.move_to(perp_line.get_center())
        proj_label.shift((0.2*UP + 1.5*RIGHT))



        self.play(Create(s0_vector), Write(s0_label))
        self.play(Create(ref_line), Create(theta_angle), Write(theta_label))
        self.wait(1)
        self.play(Create(s_0_dashed_line), Create(perp_line),run_time = 1)
        self.play(Create(right_angle), Write(proj_label), run_time=1)
        self.wait(1)
        # --- 7. EQUATIONS ---
        delay_eq = MathTex(
            r"\tau = \frac{\vec{b} \cdot \hat{s}_0}{c} = \frac{b \cos\theta}{c}"
        ).to_corner(UL)
        
        electric_field_eq = MathTex(r"\vec{E}(t,z) = -E_0 e^{i(\vec{k}\cdot\hat{s}_0 - \omega t)}\hat{s}_0").to_corner(UR)

        self.play(Write(delay_eq))
        self.wait(1)
        self.play(Write(electric_field_eq))
        self.wait(2)
        
        self.play(FadeOut(delay_eq), FadeOut(electric_field_eq))
        self.wait(1)

        v1_eq = MathTex(r"V_1 = V_0 \cos(\omega(t-\tau))").scale(0.8)
        v2_eq = MathTex(r"V_2 = V_0 \cos(\omega t )").scale(0.8)
        
        voltages = VGroup(v1_eq, v2_eq).arrange(DOWN, aligned_edge=LEFT, buff=0.4).to_corner(UL)

        self.play(Write(voltages))
        self.wait(2)

        correlator_eq = MathTex(
            r"\langle V_1 \ast V_2 \rangle = \langle V_0^2 \cos(\omega t) \cos(\omega(t-\tau))\rangle"
        ).scale(0.8).to_corner(UL)

        corr_eq_2 = MathTex(
            r"\langle V_1 \ast V_2 \rangle = \langle \frac{V_0^2}{2} [ \cos(\omega \tau) + \cos(2\omega t - \omega\tau) ] \rangle"
        ).scale(0.8).to_corner(UL)

        corr_eq_3 = MathTex(
            r"\langle V_1 \ast V_2 \rangle = \frac{V_0^2}{2} \cos(\omega \tau)"
        ).scale(0.8).to_corner(UL)
        
        corr_eq_4 = MathTex(
            r"\langle V_1 \ast V_2 \rangle = \frac{V_0^2}{2} \cos\left(\omega \frac{b \cos\theta}{c}\right)"
        ).scale(0.8).to_corner(UL)
        
        self.play(ReplacementTransform(voltages, correlator_eq))
        self.wait(1.5)
        self.play(ReplacementTransform(correlator_eq, corr_eq_2))
        self.wait(1.5)
        self.play(ReplacementTransform(corr_eq_2, corr_eq_3))
        self.wait(1.5)
        self.play(ReplacementTransform(corr_eq_3, corr_eq_4))
        self.wait(3)
        self.play(FadeOut(corr_eq_4))

        # --- 8. FINAL ZOOM & SKY DOME FRINGES ---
        
        # Group literally everything currently on screen together
        full_system = VGroup(
            observatory, correlator, wire1, wire2, v1_label, v2_label,
            s0_vector, s0_label, ref_line, theta_angle, theta_label, s_0_dashed_line, perp_line, proj_label,right_angle
        )
        
        # Shrink the dots moving forward, scale the system, and push it to the bottom
        signal_manager.dot_scale = 0.5 
        self.play(full_system.animate.scale(0.5).to_edge(DOWN, buff=0.5))
        self.wait(1)

        # Calculate the mathematical center for the dome
        midpoint = (self.a1.get_start() + self.a2.get_start()) / 2
        R = 5.2
        
        dome = DashedVMobject(Arc(radius=R, start_angle=0, angle=PI, arc_center=midpoint), num_dashes=40)
        dome.set_color(GRAY)
        dome_label = Text("Sky", color=GRAY, font_size=24).next_to(dome, UP, buff=0.2)
        
        self.play(Create(dome), Write(dome_label))
        
        # Create the fringe lobe pattern
        # k acts as the spatial frequency term (omega * b / c)
        b_i = 16
        nu = 9e8
        k = b_i 
        amplitude = 0.5 

        w_eq = MathTex(r"\nu = 900 \text{ MHz}", color = YELLOW)
        b_eq = MathTex(r"b = 16 \text{ m}", color = YELLOW)
        
        params = VGroup(w_eq, b_eq).arrange(DOWN, aligned_edge=LEFT, buff=0.4).to_corner(UL)

        # FIXED: Removed the [] brackets inside Write()
        self.play(Write(params)) 
        self.wait(2)
        
        def fringe_func(t):
            # Polar equation for the interference lobes mapped onto the dome radius
            r = R + amplitude * np.cos(k * np.cos(t))
            return midpoint + np.array([r * np.cos(t), r * np.sin(t), 0])

        # FIXED: Added 0.005 to t_range. This is the 'dt' step size. 
        # Without this tiny step size, k=300 will look like a jagged, broken line!
        fringes = ParametricFunction(fringe_func, t_range=[0, PI, 0.005], color=YELLOW)
        
        fringe_eq_label = MathTex(r"\text{Fringe rate} \propto \cos\left(\frac{\omega b \cos\theta}{c}\right)", color=WHITE)
        fringe_eq_label.move_to(midpoint + np.array([(R - 3.2) * np.cos(PI/2), (R - 3.2) * np.sin(PI/2), 0]))

        fringe_res_eq = MathTex(r"\text{Angular Resolution of Interferometer} \propto \frac{\lambda}{b}", color=WHITE).scale(0.75)
        fringe_res_eq_2 = MathTex(r"\Delta \theta \propto \frac{\lambda}{b}", color=WHITE).scale(0.75).to_corner(UL)

        # FIXED: Consolidated run_time to the main play call so the Create and Write sync up
        self.play(Create(fringes), Write(fringe_eq_label), run_time=3)
        self.wait(2)
        self.play(ReplacementTransform(fringe_eq_label,fringe_res_eq))

        b_1 = 96
        k = b_1 
        amplitude = 0.5 

        w_eq_2 = MathTex(r"\nu = 900 \text{ MHz}", color=RED)
        b_eq_2 = MathTex(r"b = 96 \text{ m}", color = RED)
        
        params_2 = VGroup(w_eq_2, b_eq_2).arrange(DOWN, aligned_edge=LEFT, buff=0.4).to_corner(UR)

        self.play(Write(params_2)) 
        self.wait(2)
        
        def fringe_func(t):
            # Polar equation for the interference lobes mapped onto the dome radius
            r = R + amplitude * np.cos(k * np.cos(t))
            return midpoint + np.array([r * np.cos(t), r * np.sin(t), 0])

        # FIXED: Added 0.005 to t_range. This is the 'dt' step size. 
        # Without this tiny step size, k=300 will look like a jagged, broken line!
        fringes_2 = ParametricFunction(fringe_func, t_range=[0, PI, 0.005], color=RED)

        # FIXED: Consolidated run_time to the main play call so the Create and Write sync up
        self.play(Create(fringes_2, run_time=3), FadeOut(dome_label, run_time=0.5))
        self.wait(5)

        self.play(FadeOut(fringes), FadeOut(params))
        self.wait(1)

        # 2. Modulate the fringes with a Gaussian envelope (Primary Beam)
        pointing_center = ValueTracker(0.0) 
        sigma = 0.25  # Roughly 14 degrees for the primary beam width
        
        convolved_fringes_2 = always_redraw(
            lambda: ParametricFunction(
                lambda t: midpoint + np.array([
                    (R + (amplitude * np.exp(-0.5 * ((t - pointing_center.get_value()) / sigma)**2)) * np.cos(k * np.cos(t))) * np.cos(t),
                    (R + (amplitude * np.exp(-0.5 * ((t - pointing_center.get_value()) / sigma)**2)) * np.cos(k * np.cos(t))) * np.sin(t),
                    0
                ]),
                t_range=[0, PI, 0.005],
                color=RED
            )
        )

        # --- NEW: White Gaussian Envelope Curve ---
        envelope_curve = always_redraw(
            lambda: ParametricFunction(
                lambda t: midpoint + np.array([
                    (R + amplitude * np.exp(-0.5 * ((t - pointing_center.get_value()) / sigma)**2)) * np.cos(t),
                    (R + amplitude * np.exp(-0.5 * ((t - pointing_center.get_value()) / sigma)**2)) * np.sin(t),
                    0
                ]),
                # Dynamically clamp the domain so it only draws a short arc over the bump
                t_range=[
                    max(0.0, pointing_center.get_value() - 2.5 * sigma), 
                    min(PI, pointing_center.get_value() + 2.5 * sigma), 
                    0.01
                ],
                color=WHITE,
                stroke_width=4
            )
        )
        helper_text = Text("Fringes are modulated by the primary beam of the dish.",color=WHITE).scale(0.45)
        self.play(ReplacementTransform(fringe_res_eq,fringe_res_eq_2),run_time=1)
        self.wait(1)
        self.play(Write(helper_text),run_time=1)
        # self.play(ReplacementTransform(fringe_eq_label,helper_text),run_time=1)
        self.wait(2)
        # Seamlessly swap the static fringes for the dynamically modulated ones
        self.add(convolved_fringes_2, envelope_curve)
        self.remove(fringes_2)
        
        # Animate the beam sweeping from the horizon (0) to PI/4
        self.play(pointing_center.animate.set_value(PI/4), run_time=4, rate_func=smooth)
        
        # Stop for 2 seconds at PI/4
        self.wait(2)
        
        # Continue animating from PI/4 to PI
        self.play(pointing_center.animate.set_value(PI/2), run_time=6, rate_func=smooth)
        self.wait(1)

        # 3. Add the double-sided arrow for the Primary Beam width
        # Dynamically grabs the final pointing center (PI) so it aligns perfectly
        final_angle = pointing_center.get_value()
        beam_arrow = DoubleArrow(
            start=midpoint + np.array([(R - 0.8) * np.cos(final_angle + 1.5*sigma), (R - 0.8) * np.sin(final_angle + 1.5*sigma), 0]),
            end=midpoint + np.array([(R - 0.8) * np.cos(final_angle - 1.5*sigma), (R - 0.8) * np.sin(final_angle - 1.5*sigma), 0]),
            buff=0, color=WHITE
        )
        
        # Position the label relative to the arrow's new orientation on the left horizon
        beam_label = Text("Primary beam of Dish", font_size=24, color=WHITE).next_to(beam_arrow, DOWN, buff=0.1)

        self.play(Create(beam_arrow), Write(beam_label))
        self.wait(5)

        # Adding more baselines (antennas)

        self.play(FadeOut(beam_arrow), FadeOut(beam_label))
        
        # Cleanup the signal flow and correlator elements safely
        signal_manager.clear_updaters() # CRITICAL: Stop the background updater first
        self.play(
            FadeOut(correlator), FadeOut(wire1), FadeOut(wire2),
            FadeOut(v1_label), FadeOut(v2_label), FadeOut(signal_dots),
            FadeOut(params_2), FadeOut(convolved_fringes_2), FadeOut(envelope_curve)
        )
        self.wait(1)

        # 2. Add the 3rd Antenna (1/3 of the distance between existing antennas)
        # We grab the current on-screen coordinates of the zoomed-out antennas
        p1_current = self.a1.get_start()
        p2_current = self.a2.get_start()
        
        # A simple vector translation from antenna 1
        vec_to_p3 = (p2_current - p1_current) * (1.0 / 3.0)
        
        # Because we copy a1, it automatically inherits the scale and positioning of the zoom!
        a3 = self.a1.copy()
        dish3 = self.dish1.copy()
        antenna3 = VGroup(a3, dish3)
        antenna3.shift(vec_to_p3)
        
        self.play(FadeIn(antenna3))
        self.wait(1)

        baselines_text = MathTex(r"\text{Number of Baselines = } \frac{N(N-1)}{2}").scale(0.5).to_corner(UR)
        
        three_baselines_text = MathTex(
            r"\text{3 antennas, 3 baselines (32 m, 64 m, 96 m)}", 
            color=WHITE
        ).scale(0.75)
        
        self.play(Write(baselines_text), ReplacementTransform(helper_text, three_baselines_text), run_time=2)
        self.wait(1)

        # 4. Math for the 3 individual baselines and the synthesized beam
        b_32 = 32
        b_64 = 64
        b_96 = 96
        
        # Calculate spatial frequencies
        k_32 = b_32 
        k_64 = b_64
        k_96 = b_96 
        
        pc = PI / 2  # The primary beam stopped at Zenith in the previous step
        
        # Helper functions to draw the modulated fringes for each baseline
        def f_32(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_32 * np.cos(t))
        def f_64(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_64 * np.cos(t))
        def f_96(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_96 * np.cos(t))
        
        # The Synthesized Beam is the average (sum) of the individual interference patterns
        def f_synth(t): 
            envelope = np.exp(-0.5 * ((t - pc) / sigma)**2)
            wave_sum = np.cos(k_32 * np.cos(t)) + np.cos(k_64 * np.cos(t)) + np.cos(k_96 * np.cos(t))
            return R + (amplitude / 3) * envelope * wave_sum

        # 5. Create the Parametric Curves (dt=0.001 is required here to prevent visual aliasing)
        fringe_32_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_32(t) * np.cos(t), f_32(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=BLUE, stroke_opacity=0.3
        )
        fringe_64_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_64(t) * np.cos(t), f_64(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=GREEN, stroke_opacity=0.3
        )
        fringe_96_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_96(t) * np.cos(t), f_96(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=RED, stroke_opacity=0.3
        )
        
        synth_beam_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_synth(t) * np.cos(t), f_synth(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=WHITE, stroke_width=4
        )

        synth_half_width = 0.035 
        
        # Position the arrow slightly above the maximum height of the synthesized peak
        arrow_radius = R + (amplitude / 3) - 0.7
        
        synth_arrow = DoubleArrow(
            start=midpoint + np.array([arrow_radius * np.cos(pc + synth_half_width), arrow_radius * np.sin(pc + synth_half_width), 0]),
            end=midpoint + np.array([arrow_radius * np.cos(pc - synth_half_width), arrow_radius * np.sin(pc - synth_half_width), 0]),
            buff=0, color=WHITE
        )
        
        # Add the label just above the new arrow
        synth_label = Text("Synthesized beam", font_size=20, color=WHITE).next_to(synth_arrow, DOWN, buff=0.1)

        # 6. Play the final sequence
        self.play(
            Create(fringe_32_curve),
            Create(fringe_64_curve),
            Create(fringe_96_curve),
            run_time=3
        )
        self.wait(1)
        
        # Draw the curve, the arrow, and the text all together
        self.play(
            Create(synth_beam_curve),
            FadeOut(fringe_32_curve, run_time=0.5),
            FadeOut(fringe_64_curve,run_time=0.5),
            FadeOut(fringe_96_curve,run_time=0.5), 
            Create(synth_arrow),
            Write(synth_label), 
            run_time=3
        )
        self.wait(3)

        # Adding a fourth antenna

        self.play(FadeOut(synth_beam_curve), FadeOut(synth_label), FadeOut(synth_arrow))

        p1_current = self.a1.get_start()
        p2_current = self.a2.get_start()
        
        # A simple vector translation from antenna 1
        vec_to_p4 = (p2_current - p1_current) * (1.0 / 2.0)
        
        # Because we copy a1, it automatically inherits the scale and positioning of the zoom!
        a4 = self.a1.copy()
        dish4 = self.dish1.copy()
        antenna4 = VGroup(a4, dish4)
        antenna4.shift(vec_to_p4)
    
        self.play(FadeIn(antenna4))
        self.wait(1)

        # Text 
        four_baselines_text = MathTex(
            r"\text{4 antennas, 6 baselines (16 m, 32 m, 48 m, 48 m, 64 m, 96 m)}", 
            color=WHITE
        ).scale(0.65)
        
        self.play(ReplacementTransform(three_baselines_text, four_baselines_text))
        self.wait(1)

        # 4. Math for the 3 individual baselines and the synthesized beam
        b_16 = 16
        b_32 = 32
        b_48 = 48
        b_64 = 64
        b_96 = 96
        
        # Calculate spatial frequencies
        k_16 = b_16
        k_32 = b_32 
        k_48 = b_48
        k_64 = b_64
        k_96 = b_96 
        
        pc = PI / 2  # The primary beam stopped at Zenith in the previous step
        
        # Helper functions to draw the modulated fringes for each baseline
        def f_16(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_16 * np.cos(t))
        def f_32(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_32 * np.cos(t))
        def f_48(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_48 * np.cos(t))
        def f_64(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_64 * np.cos(t))
        def f_96(t): return R + amplitude * np.exp(-0.5 * ((t - pc) / sigma)**2) * np.cos(k_96 * np.cos(t))
        
        # The Synthesized Beam is the average (sum) of the individual interference patterns
        def f_synth(t): 
            envelope = np.exp(-0.5 * ((t - pc) / sigma)**2)
            wave_sum = np.cos(k_16 * np.cos(t)) + np.cos(k_32 * np.cos(t)) + 2*np.cos(k_48 * np.cos(t)) + np.cos(k_64 * np.cos(t)) + np.cos(k_96 * np.cos(t))
            return R + (amplitude/6) * envelope * wave_sum

        # 5. Create the Parametric Curves (dt=0.001 is required here to prevent visual aliasing)
        fringe_16_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_16(t) * np.cos(t), f_16(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=PURPLE, stroke_opacity=0.3
        )
        fringe_32_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_32(t) * np.cos(t), f_32(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=BLUE, stroke_opacity=0.3
        )
        fringe_48_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_48(t) * np.cos(t), f_48(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=TEAL, stroke_opacity=0.3
        )
        fringe_64_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_64(t) * np.cos(t), f_64(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=GREEN, stroke_opacity=0.3
        )
        fringe_96_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_96(t) * np.cos(t), f_96(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=RED, stroke_opacity=0.3
        )
        
        synth_beam_curve = ParametricFunction(
            lambda t: midpoint + np.array([f_synth(t) * np.cos(t), f_synth(t) * np.sin(t), 0]),
            t_range=[0, PI, 0.001], color=WHITE, stroke_width=4
        )

        synth_half_width = 0.035 
        
        # Position the arrow slightly above the maximum height of the synthesized peak
        arrow_radius = R + (amplitude/6) - 0.7
        
        synth_arrow = DoubleArrow(
            start=midpoint + np.array([arrow_radius * np.cos(pc + synth_half_width), arrow_radius * np.sin(pc + synth_half_width), 0]),
            end=midpoint + np.array([arrow_radius * np.cos(pc - synth_half_width), arrow_radius * np.sin(pc - synth_half_width), 0]),
            buff=0, color=WHITE
        )
        
        # Add the label just above the new arrow
        synth_label = Text("Synthesized beam", font_size=20, color=WHITE).next_to(synth_arrow, DOWN, buff=0.1)

        # 6. Play the final sequence
        self.play(
            Create(fringe_16_curve),
            Create(fringe_32_curve),
            Create(fringe_48_curve),
            Create(fringe_64_curve),
            Create(fringe_96_curve),
            run_time=5
        )
        self.wait(1)
        
        # Draw the curve, the arrow, and the text all together
        self.play(
            Create(synth_beam_curve),
            FadeOut(fringe_16_curve, run_time=0.5),
            FadeOut(fringe_32_curve, run_time=0.5),
            FadeOut(fringe_48_curve, run_time=0.5),
            FadeOut(fringe_64_curve,run_time=0.5),
            FadeOut(fringe_96_curve,run_time=0.5), 
            Create(synth_arrow),
            Write(synth_label), 
            run_time=3
        )
        self.wait(5)


