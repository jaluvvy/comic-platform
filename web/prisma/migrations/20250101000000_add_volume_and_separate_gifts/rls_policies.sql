-- Enable RLS on new tables
ALTER TABLE "volumes" ENABLE ROW LEVEL SECURITY;

-- Volumes: public read, admin write
CREATE POLICY "Public can view volumes" ON "volumes" FOR SELECT USING (true);
CREATE POLICY "Admins can manage volumes" ON "volumes" FOR ALL USING (auth.role() = 'authenticated');

-- Gifts: public read, admin write
CREATE POLICY "Public can view gifts" ON "gifts" FOR SELECT USING (true);
CREATE POLICY "Admins can manage gifts" ON "gifts" FOR ALL USING (auth.role() = 'authenticated');

-- Events: public read, admin write
CREATE POLICY "Public can view events" ON "events" FOR SELECT USING (true);
CREATE POLICY "Admins can manage events" ON "events" FOR ALL USING (auth.role() = 'authenticated');

-- EventGifts: public read, admin write
CREATE POLICY "Public can view event_gifts" ON "event_gifts" FOR SELECT USING (true);
CREATE POLICY "Admins can manage event_gifts" ON "event_gifts" FOR ALL USING (auth.role() = 'authenticated');

-- Users: users can view own, admin can view all
CREATE POLICY "Users can view own profile" ON "users" FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Admins can view all users" ON "users" FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can update own profile" ON "users" FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Admins can manage users" ON "users" FOR ALL USING (auth.role() = 'authenticated');

-- Listings: public read active, users can manage own
CREATE POLICY "Public can view active listings" ON "listings" FOR SELECT USING (status = 'active');
CREATE POLICY "Users can view own listings" ON "listings" FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create listings" ON "listings" FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own listings" ON "listings" FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own listings" ON "listings" FOR DELETE USING (auth.uid() = user_id);
